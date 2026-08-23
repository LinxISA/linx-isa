#!/usr/bin/env python3
"""Build and run the exact PTO 0.58.3 CUBE corpus as initramfs PID1 children."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import selectors
import shlex
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

PTO_KERNELS_COMMIT = "322443efed141211d1c296f159b1131d384a1f44"
TILEOP_COMMIT = "1e63705463227598c445cef96755e6e7b85db2e2"
LLVM_COMMIT = "b7c83f68bf84125e696a70bec4b665c70a3b584d"
QEMU_COMMIT = "8fec88096d57efcd4a921fb3f925e7defb4c0d09"
LINUX_COMMIT = "1055a743f16eaebfc371e0aabec8c861ab44858f"
PTO_RELEASE = "0.58.3"
PTO_PROJECTION = "8a48b80e04484c70870f155bf9efc79d2a805cf99e809f4e4e8a7e6a7eb34172"
PTO_CONTENT = "f299fe3d256c5d071e57bb4aaa2be2de2e4a386ae090048df1f73ae92d392678"

CUBE_CASES = (
    "tmatmul_acc_fp32_32x32x32",
    "tmatmul_bias_fp16_32x64x64",
    "tmatmul_bias_fp32_32x32x32",
    "tmatmul_fp16_16x32x32",
    "tmatmul_fp16_32x64x64",
    "tmatmul_fp32_32x32x32",
)
ALLOWED_NEEDED = {"libc.so", "libm.so"}


class GateError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_evidence(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size,
    }


def _git_value(root: Path, expression: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", expression],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise GateError(f"cannot resolve git identity {expression} under {root}") from error


def _git_dirty(root: Path) -> bool:
    output = subprocess.check_output(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
        text=True,
    )
    return bool(output.strip())


def _require_git_identity(root: Path, expected: str, *, allow_same_tree: bool) -> dict[str, Any]:
    head = _git_value(root, "HEAD")
    head_tree = _git_value(root, "HEAD^{tree}")
    expected_tree = _git_value(root, f"{expected}^{{tree}}")
    if _git_dirty(root):
        raise GateError(f"tracked source is dirty: {root}")
    if head != expected and not (allow_same_tree and head_tree == expected_tree):
        raise GateError(
            f"source identity mismatch: root={root} head={head} expected={expected} "
            f"head_tree={head_tree} expected_tree={expected_tree}"
        )
    return {
        "path": str(root.resolve()),
        "head": head,
        "tree": head_tree,
        "expected_commit": expected,
        "expected_tree": expected_tree,
        "same_tree_as_expected": head_tree == expected_tree,
        "dirty_tracked": False,
    }


def _require_tool_commit(tool: Path, expected: str) -> dict[str, Any]:
    output = subprocess.check_output([str(tool), "--version"], text=True)
    if expected not in output:
        raise GateError(f"tool does not report expected commit {expected}: {tool}")
    evidence = _file_evidence(tool)
    evidence["version"] = output.splitlines()[0] if output.splitlines() else ""
    evidence["expected_commit"] = expected
    return evidence


def _run(cmd: list[str], *, cwd: Path, log: Path, env: dict[str, str] | None = None) -> None:
    with log.open("w", encoding="utf-8") as stream:
        stream.write("+ " + shlex.join(cmd) + "\n")
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if result.returncode != 0:
        raise GateError(f"command failed with exit {result.returncode}: {shlex.join(cmd)} (log: {log})")


def _parse_needed(readelf: Path, elf: Path) -> set[str]:
    output = subprocess.check_output([str(readelf), "-d", str(elf)], text=True)
    return set(re.findall(r"Shared library: \[([^]]+)\]", output))


def _validate_pto_identity(
    parser: Path,
    files: list[Path],
    out_dir: Path,
    *,
    log_name: str = "pto_identity.log",
) -> dict[str, Any]:
    log = out_dir / log_name
    records: dict[str, Any] = {}
    with log.open("w", encoding="utf-8") as stream:
        for path in files:
            result = subprocess.run(
                [sys.executable, str(parser), str(path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            text = result.stdout.decode("utf-8", errors="replace")
            stream.write(f"{path}: {text}")
            if result.returncode != 0:
                raise GateError(f"PTO identity validation failed: {path} (log: {log})")
            records[path.name] = _file_evidence(path)
    return {"parser": _file_evidence(parser), "files": records, "log": str(log)}


def _validate_lock(pto_root: Path) -> dict[str, Any]:
    path = pto_root / "PTO_ISA.lock.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "release": PTO_RELEASE,
        "encoding_projection_sha256": PTO_PROJECTION,
        "content_sha256": PTO_CONTENT,
    }
    mismatches = {key: data.get(key) for key, value in expected.items() if data.get(key) != value}
    if mismatches:
        raise GateError(f"PTO lock mismatch: {mismatches}")
    return {"file": _file_evidence(path), "identity": expected}


def _require_empty_output(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise GateError(f"PTO build output must be absent or empty: {path}")
    path.mkdir(parents=True, exist_ok=True)


def _build_cube_elves(
    pto_root: Path,
    build_output: Path,
    clang: Path,
    tileop_root: Path,
    sysroot: Path,
    out_dir: Path,
) -> tuple[list[Path], dict[str, Any]]:
    _require_empty_output(build_output)
    compile_all = pto_root / "benchmarks" / "supernpu" / "microbenchmark" / "cube" / "compile.all"
    env = os.environ.copy()
    env.update(
        {
            "MAKEFLAGS": f"OBJ_ROOT={build_output}",
            "COMPILER_DIR": str(clang.parent),
            "LINX_TILEOP_API_ROOT": str(tileop_root),
            "LINX_SYSROOT": str(sysroot),
        }
    )
    _run(["bash", str(compile_all)], cwd=compile_all.parent, log=out_dir / "pto_cube_build.log", env=env)
    elf_dir = build_output / "microbenchmark" / "cube" / "elf" / "cube"
    elves = [elf_dir / f"{name}.elf" for name in CUBE_CASES]
    missing = [str(path) for path in elves if not path.is_file()]
    if missing:
        raise GateError(f"missing CUBE ELF outputs: {missing}")
    return elves, {path.name: _file_evidence(path) for path in elves}


def _compile_init(
    source: Path,
    output: Path,
    clang: Path,
    sysroot: Path,
    out_dir: Path,
) -> dict[str, Any]:
    obj = out_dir / "pto_cube_init.o"
    runtime = sysroot / "lib" / "liblinx_builtin_rt.a"
    compile_cmd = [
        str(clang), "-target", "linx64-unknown-linux-musl", "--sysroot", str(sysroot),
        "-fPIE", "-O2", "-c", str(source), "-o", str(obj),
    ]
    link_cmd = [
        str(clang), "-target", "linx64-unknown-linux-musl", "--sysroot", str(sysroot),
        "-static", "-Wl,-pie", "-fuse-ld=lld", "-nostdlib",
        str(sysroot / "lib" / "rcrt1.o"), str(sysroot / "lib" / "crti.o"),
        str(obj), str(runtime), str(sysroot / "lib" / "libc.a"),
        str(sysroot / "lib" / "crtn.o"), "-Wl,--image-base=0x40000000", "-o", str(output),
    ]
    env = os.environ.copy()
    env["PATH"] = f"{clang.parent}:{env.get('PATH', '')}"
    _run(compile_cmd, cwd=REPO_ROOT, log=out_dir / "pto_cube_init_compile.log", env=env)
    _run(link_cmd, cwd=REPO_ROOT, log=out_dir / "pto_cube_init_link.log", env=env)
    return _file_evidence(output)


def _initramfs_lines(init: Path, elves: list[Path], libc: Path) -> list[str]:
    lines = [
        "dir /dev 0755 0 0",
        "nod /dev/console 0600 0 0 c 5 1",
        "nod /dev/null 0666 0 0 c 1 3",
        "nod /dev/ttyS0 0600 0 0 c 4 64",
        "dir /proc 0755 0 0",
        "dir /sys 0755 0 0",
        "dir /tmp 1777 0 0",
        "dir /lib 0755 0 0",
        "dir /pto_cube 0755 0 0",
        f"file /init {init} 0755 0 0",
        f"file /lib/libc.so {libc} 0755 0 0",
        f"file /lib/libm.so {libc} 0755 0 0",
        f"file /lib/ld-musl-linx64.so.1 {libc} 0755 0 0",
    ]
    lines.extend(f"file /pto_cube/{path.name} {path} 0755 0 0" for path in elves)
    lines.append("")
    return lines


def _classify_runtime(text: str, returncode: int, timed_out: bool) -> tuple[bool, str, str]:
    start = "PTO_CUBE_START count=6" in text
    passed = "PTO_CUBE_PASS count=6" in text
    case_passes = sum(f"PTO_CUBE_CASE_PASS {name} value=0" in text for name in CUBE_CASES)
    fail_line = next((line for line in text.splitlines() if line.startswith("PTO_CUBE_CASE_FAIL")), "")
    breakpoint_line = next(
        (line for line in text.splitlines() if line.startswith("Linx: EBREAK trap")),
        "",
    )
    if fail_line:
        return False, "runtime_case_failure", fail_line
    if breakpoint_line and not start:
        return False, "runtime_kernel_breakpoint", breakpoint_line
    if timed_out:
        return False, "runtime_timeout", f"timeout: start={start} case_passes={case_passes} pass={passed}"
    if returncode != 0:
        return False, "runtime_qemu_exit_failure", f"qemu_rc={returncode} case_passes={case_passes}"
    if not start or not passed or case_passes != len(CUBE_CASES):
        return False, "runtime_missing_marker", (
            f"start={start} case_passes={case_passes}/{len(CUBE_CASES)} pass={passed}"
        )
    if "LINX_REBOOT lisc_shutdown" not in text:
        return False, "runtime_missing_shutdown", "pass markers observed without LINX_REBOOT lisc_shutdown"
    return True, "runtime_pass", f"all {len(CUBE_CASES)} cases passed and powered off"


def _run_qemu_bounded(
    command: list[str],
    log: Path,
    timeout: int,
) -> tuple[int, bool, str]:
    """Stream QEMU output and stop a repeated pre-PID1 breakpoint loop."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout
    breakpoints: Counter[str] = Counter()
    observed: list[str] = []
    timed_out = False

    with log.open("w", encoding="utf-8") as stream:
        while process.poll() is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                process.terminate()
                break
            events = selector.select(timeout=min(0.25, remaining))
            for key, _ in events:
                line = key.fileobj.readline()
                if not line:
                    continue
                stream.write(line)
                if (
                    "PTO_CUBE" in line
                    or "LINX_REBOOT" in line
                    or "Kernel panic" in line
                    or "Linx: EBREAK trap" in line
                ):
                    observed.append(line.rstrip())
                if line.startswith("Linx: EBREAK trap") and not any(
                    item.startswith("PTO_CUBE_START") for item in observed
                ):
                    diagnostic = line.strip()
                    breakpoints[diagnostic] += 1
                    if breakpoints[diagnostic] >= 8:
                        process.terminate()
                        break

        try:
            returncode = process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            returncode = process.wait(timeout=2)

        for line in process.stdout:
            stream.write(line)
            if "PTO_CUBE" in line or "LINX_REBOOT" in line or "Kernel panic" in line:
                observed.append(line.rstrip())

    selector.close()
    return (124 if timed_out else returncode), timed_out, "\n".join(observed)


def _write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pto-kernels-root", required=True)
    parser.add_argument("--pto-build-output", required=True)
    parser.add_argument("--tileop-root", required=True)
    parser.add_argument("--sysroot", required=True)
    parser.add_argument("--clang", required=True)
    parser.add_argument("--kernel", required=True)
    parser.add_argument("--linux-source-root", required=True)
    parser.add_argument("--qemu", required=True)
    parser.add_argument("--qemu-source-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument(
        "--append",
        default="lpj=1000000 loglevel=1 console=ttyS0 kfence.sample_interval=0",
    )
    args = parser.parse_args(argv)

    paths = {
        name: Path(value).expanduser().resolve()
        for name, value in vars(args).items()
        if name not in {"timeout", "append"}
    }
    out_dir = paths["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "summary.json"
    summary: dict[str, Any] = {
        "schema_version": "pto-cube-system-v1",
        "result": {"ok": False, "classification": "not_run"},
        "paths": {name: str(path) for name, path in paths.items()},
        "expected": {
            "pto_kernels": PTO_KERNELS_COMMIT,
            "tileop": TILEOP_COMMIT,
            "llvm": LLVM_COMMIT,
            "qemu": QEMU_COMMIT,
            "linux": LINUX_COMMIT,
        },
        "stages": [],
    }

    def stage(name: str, status: str, detail: str, log: Path | None = None) -> None:
        record = {"name": name, "status": status, "detail": detail}
        if log is not None:
            record["log"] = str(log)
        summary["stages"].append(record)
        _write_summary(summary_path, summary)

    try:
        for name in ("pto_kernels_root", "tileop_root", "sysroot", "linux_source_root", "qemu_source_root"):
            if not paths[name].is_dir():
                raise GateError(f"required directory not found: {paths[name]}")
        for name in ("clang", "kernel", "qemu"):
            if not paths[name].is_file():
                raise GateError(f"required file not found: {paths[name]}")

        provenance = {
            "pto_kernels": _require_git_identity(paths["pto_kernels_root"], PTO_KERNELS_COMMIT, allow_same_tree=False),
            "tileop": _require_git_identity(paths["tileop_root"], TILEOP_COMMIT, allow_same_tree=False),
            "linux": _require_git_identity(paths["linux_source_root"], LINUX_COMMIT, allow_same_tree=True),
            "qemu": _require_git_identity(paths["qemu_source_root"], QEMU_COMMIT, allow_same_tree=True),
            "clang": _require_tool_commit(paths["clang"], LLVM_COMMIT),
            "kernel": _file_evidence(paths["kernel"]),
            "qemu_binary": _file_evidence(paths["qemu"]),
            "pto_lock": _validate_lock(paths["pto_kernels_root"]),
        }
        qemu_root = paths["qemu_source_root"]
        try:
            paths["qemu"].relative_to(qemu_root)
        except ValueError as error:
            raise GateError("QEMU binary must be inside the verified QEMU source/build root") from error
        summary["provenance"] = provenance
        stage("provenance", "pass", "all source/tool identities are exact or squash-tree equivalent")

        elves, elf_evidence = _build_cube_elves(
            paths["pto_kernels_root"], paths["pto_build_output"], paths["clang"],
            paths["tileop_root"], paths["sysroot"], out_dir,
        )
        summary["elves"] = elf_evidence
        stage("pto-cube-build", "pass", f"built {len(elves)} exact CUBE ELFs", out_dir / "pto_cube_build.log")

        identity_parser = paths["tileop_root"] / "test" / "tileop_api" / "verify_pto_identity.py"
        libc = paths["sysroot"] / "lib" / "libc.so"
        loader = paths["sysroot"] / "lib" / "ld-musl-linx64.so.1"
        if not libc.is_file() or not loader.exists():
            raise GateError("phase-C sysroot is missing libc.so or ld-musl-linx64.so.1")
        summary["pto_identity"] = _validate_pto_identity(identity_parser, [*elves, libc, loader], out_dir)
        readelf = paths["clang"].parent / "llvm-readelf"
        needed = {path.name: sorted(_parse_needed(readelf, path)) for path in elves}
        unexpected = {name: libs for name, libs in needed.items() if not set(libs) <= ALLOWED_NEEDED}
        if unexpected:
            raise GateError(f"unsupported DT_NEEDED libraries: {unexpected}")
        summary["needed"] = needed
        stage("pto-identity", "pass", "six ELFs plus loader/libc match exact PTO 0.58.3 identity")

        init = out_dir / "pto_cube_init"
        summary["init"] = _compile_init(
            SCRIPT_DIR / "tests" / "linux_musl_pto_cube_init.c",
            init,
            paths["clang"],
            paths["sysroot"],
            out_dir,
        )
        summary["init_identity"] = _validate_pto_identity(
            identity_parser, [init], out_dir, log_name="pto_init_identity.log"
        )
        stage("init-build", "pass", "built static PTO CUBE PID1 runner")

        gen_init_cpio = paths["kernel"].parent / "usr" / "gen_init_cpio"
        if not gen_init_cpio.is_file() or not os.access(gen_init_cpio, os.X_OK):
            raise GateError(f"kernel-matched gen_init_cpio not found: {gen_init_cpio}")
        initramfs_list = out_dir / "initramfs.list"
        initramfs = out_dir / "initramfs.cpio"
        initramfs_list.write_text("\n".join(_initramfs_lines(init, elves, libc)), encoding="utf-8")
        _run(
            [str(gen_init_cpio), "-o", str(initramfs), str(initramfs_list)],
            cwd=out_dir,
            log=out_dir / "initramfs.log",
        )
        summary["initramfs"] = _file_evidence(initramfs)
        stage("initramfs", "pass", "packaged PID1, six ELFs, loader, libc, and libm")

        qemu_cmd = [
            str(paths["qemu"]), "-machine", "virt", "-nographic", "-monitor", "none",
            "-no-reboot", "-d", "guest_errors", "-kernel", str(paths["kernel"]),
            "-initrd", str(initramfs), "-append", args.append, "-bios", "none",
        ]
        qemu_log = out_dir / "qemu.log"
        returncode, timed_out, text = _run_qemu_bounded(qemu_cmd, qemu_log, args.timeout)
        ok, classification, detail = _classify_runtime(text, returncode, timed_out)
        summary["runtime"] = {
            "command": shlex.join(qemu_cmd),
            "returncode": returncode,
            "timed_out": timed_out,
            "classification": classification,
            "detail": detail,
            "log": str(qemu_log),
        }
        stage("qemu-system", "pass" if ok else "fail", detail, qemu_log)
        summary["result"] = {"ok": ok, "classification": classification}
        _write_summary(summary_path, summary)
        if not ok:
            print(f"error: PTO CUBE system gate failed: {detail} ({summary_path})", file=sys.stderr)
            return 2
        print(f"ok: PTO CUBE system gate passed ({summary_path})")
        return 0
    except (GateError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        stage("gate", "fail", str(error))
        summary["result"] = {"ok": False, "classification": "gate_failure", "detail": str(error)}
        _write_summary(summary_path, summary)
        print(f"error: {error} ({summary_path})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
