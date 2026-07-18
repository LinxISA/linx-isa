#!/usr/bin/env python3
"""Run one static Linx C workload under Linux/QEMU with fail-closed evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from qemu_build_paths import require_clean_qemu_binary  # noqa: E402

INIT_SOURCE = SCRIPT_DIR / "linux_c_benchmark_init.c"
FORBIDDEN_MARKERS = (
    "Kernel panic - not syncing:",
    "LINX_USER_TRAP",
    "LINX_BENCH_EXEC_FAIL",
    "LINX_BENCH_FORK_FAIL",
    "LINX_BENCH_WAIT_FAIL",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_evidence(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size,
    }


def _check_file(path: Path, label: str, *, executable: bool = False) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise SystemExit(f"error: {label} not found: {resolved}")
    if executable and not os.access(resolved, os.X_OK):
        raise SystemExit(f"error: {label} is not executable: {resolved}")
    return resolved


def _classify(output: str, *, qemu_rc: int | None, timed_out: bool) -> dict[str, Any]:
    required = (
        "LINX_BENCH_START",
        "LINX_BENCH_EXIT rc=0",
        "LINX_REBOOT lisc_shutdown",
    )
    missing = [marker for marker in required if marker not in output]
    forbidden = [marker for marker in FORBIDDEN_MARKERS if marker in output]
    ok = not timed_out and qemu_rc == 0 and not missing and not forbidden
    return {
        "ok": ok,
        "classification": (
            "pass"
            if ok
            else (
                "timeout"
                if timed_out
                else ("qemu-exit" if qemu_rc != 0 else ("forbidden-marker" if forbidden else "missing-marker"))
            )
        ),
        "qemu_returncode": qemu_rc,
        "timed_out": timed_out,
        "missing_markers": missing,
        "forbidden_markers": forbidden,
    }


def _static_link_inputs(sysroot: Path) -> list[Path]:
    lib = sysroot / "lib"
    crt1 = lib / "rcrt1.o"
    if not crt1.is_file():
        crt1 = lib / "crt1.o"
    inputs = [
        crt1,
        lib / "crti.o",
        lib / "liblinx_builtin_rt.a",
        lib / "libc.a",
        lib / "crtn.o",
    ]
    if not inputs[2].is_file():
        inputs[2] = lib / "libclang_rt.builtins-linx64.a"
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise SystemExit("error: missing static supervisor link inputs: " + ", ".join(missing))
    return inputs


def _run_checked(command: list[str], log: Path) -> None:
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    log.write_bytes(proc.stdout or b"")
    if proc.returncode != 0:
        raise SystemExit(f"error: command failed with rc={proc.returncode}; see {log}")


def _build_supervisor(
    *, clang: Path, sysroot: Path, target: str, out_dir: Path
) -> tuple[Path, list[list[str]]]:
    obj = out_dir / "linux_c_benchmark_init.o"
    binary = out_dir / "init"
    compile_command = [
        str(clang),
        "-target",
        target,
        "--sysroot",
        str(sysroot),
        "-O2",
        "-fPIE",
        "-c",
        str(INIT_SOURCE),
        "-o",
        str(obj),
    ]
    _run_checked(compile_command, out_dir / "supervisor-compile.log")
    crt1, crti, runtime, libc, crtn = _static_link_inputs(sysroot)
    link_command = [
        str(clang),
        "-target",
        target,
        "--sysroot",
        str(sysroot),
        "-fuse-ld=lld",
        "-static",
        "-Wl,-pie,-z,now",
        "-nostdlib",
        str(crt1),
        str(crti),
        str(obj),
        str(runtime),
        str(libc),
        str(crtn),
        "-Wl,--build-id=none,--image-base=0x40000000",
        "-o",
        str(binary),
    ]
    _run_checked(link_command, out_dir / "supervisor-link.log")
    binary.chmod(binary.stat().st_mode | 0o111)
    return binary, [compile_command, link_command]


def _initramfs_lines(supervisor: Path, executable: Path) -> list[str]:
    return [
        "dir /dev 0755 0 0",
        "nod /dev/console 0600 0 0 c 5 1",
        "nod /dev/null 0666 0 0 c 1 3",
        "nod /dev/ttyS0 0600 0 0 c 4 64",
        "dir /proc 0755 0 0",
        "dir /sys 0755 0 0",
        "dir /tmp 1777 0 0",
        f"file /init {supervisor} 0755 0 0",
        f"file /bench {executable} 0755 0 0",
        "",
    ]


def _run_qemu(command: list[str], timeout: int) -> tuple[str, int | None, bool]:
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        output, _ = proc.communicate(timeout=timeout)
        return output.decode("utf-8", errors="replace"), proc.returncode, False
    except subprocess.TimeoutExpired as exc:
        proc.kill()
        output, _ = proc.communicate()
        return (output or b"").decode("utf-8", errors="replace"), None, True


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True)
    parser.add_argument("--kernel", required=True)
    parser.add_argument("--qemu", required=True)
    parser.add_argument("--sysroot", default=str(ROOT / "out" / "libc" / "musl" / "install" / "phase-b"))
    parser.add_argument("--clang", default=str(ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "clang"))
    parser.add_argument("--target", default="linx64-unknown-linux-musl")
    parser.add_argument("--gen-init-cpio", default="")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--out-root", default=os.environ.get("LINX_BENCHMARK_LAUNCH_OUT_ROOT", str(ROOT / "workloads" / "generated" / "linux-benchmark-runs")))
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        raise SystemExit("error: --timeout must be positive")

    executable = _check_file(Path(args.exe), "workload ELF", executable=True)
    kernel = _check_file(Path(args.kernel), "kernel image")
    qemu = _check_file(Path(args.qemu), "QEMU", executable=True)
    clang = _check_file(Path(args.clang), "clang", executable=True)
    sysroot = Path(args.sysroot).expanduser().resolve()
    init_source = _check_file(INIT_SOURCE, "PID1 supervisor source")
    gen_init = _check_file(
        Path(args.gen_init_cpio) if args.gen_init_cpio else kernel.parent / "usr" / "gen_init_cpio",
        "gen_init_cpio",
        executable=True,
    )
    try:
        qemu_provenance = require_clean_qemu_binary(ROOT, qemu)
    except RuntimeError as exc:
        raise SystemExit(f"error: {exc}") from exc

    out_root = Path(args.out_root).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix=f"{executable.stem}-", dir=out_root))
    supervisor, build_commands = _build_supervisor(
        clang=clang,
        sysroot=sysroot,
        target=args.target,
        out_dir=run_dir,
    )
    init_list = run_dir / "initramfs.list"
    initramfs = run_dir / "initramfs.cpio"
    init_list.write_text("\n".join(_initramfs_lines(supervisor, executable)), encoding="utf-8")
    _run_checked([str(gen_init), "-o", str(initramfs), str(init_list)], run_dir / "initramfs.log")

    qemu_command = [
        str(qemu),
        "-machine",
        "virt",
        "-nographic",
        "-monitor",
        "none",
        "-no-reboot",
        "-kernel",
        str(kernel),
        "-initrd",
        str(initramfs),
        "-append",
        "lpj=1000000 loglevel=1 console=ttyS0 kfence.sample_interval=0 init=/init",
        "-bios",
        "none",
    ]
    output, qemu_rc, timed_out = _run_qemu(qemu_command, args.timeout)
    transcript = run_dir / "transcript.txt"
    transcript.write_text(output, encoding="utf-8")
    result = _classify(output, qemu_rc=qemu_rc, timed_out=timed_out)
    report = {
        "schema_version": "linx-c-benchmark-launch-v1",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "result": result,
        "inputs": {
            "executable": _file_evidence(executable),
            "kernel": _file_evidence(kernel),
            "qemu": qemu_provenance,
            "clang": _file_evidence(clang),
            "sysroot_libc": _file_evidence(sysroot / "lib" / "libc.a"),
            "supervisor_source": _file_evidence(init_source),
            "supervisor": _file_evidence(supervisor),
            "initramfs": _file_evidence(initramfs),
        },
        "build_commands": build_commands,
        "qemu_command": qemu_command,
        "transcript": str(transcript),
    }
    report_path = run_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sys.stdout.write(output)
    print(f"LINX_BENCH_REPORT path={report_path}", file=sys.stderr)
    if result["ok"]:
        return 0
    print(f"error: benchmark launch failed: {result['classification']}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
