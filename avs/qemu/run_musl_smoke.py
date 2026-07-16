#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "bringup"))

from qemu_build_paths import qemu_binary_provenance  # noqa: E402

_EXTRA_SUMMARY_PATH: Path | None = None

SAMPLES: dict[str, dict[str, str]] = {
    "malloc_printf": {
        "src": "linux_musl_malloc_printf.c",
        "start": "MUSL_SMOKE_START",
        "pass": "MUSL_SMOKE_PASS",
    },
    "hello": {
        "src": "linux_musl_hello.c",
        "start": "HELLO_WORLD_START",
        "pass": "HELLO_WORLD_PASS",
    },
    "callret": {
        "src": "linux_musl_callret_matrix.c",
        "start": "MUSL_CALLRET_START",
        "pass": "MUSL_CALLRET_PASS",
    },
    "fork_wait": {
        "src": "linux_musl_fork_wait.c",
        "start": "MUSL_FORK_WAIT_START",
        "pass": "MUSL_FORK_WAIT_PASS",
    },
    "fork_wait_raw_exit": {
        "src": "linux_musl_fork_wait_raw_exit.c",
        "start": "MUSL_FORK_WAIT_RAW_EXIT_START",
        "pass": "MUSL_FORK_WAIT_RAW_EXIT_PASS",
    },
    "fork_noinline_raw": {
        "src": "linux_musl_fork_noinline_raw.c",
        "start": "MUSL_FORK_NOINLINE_RAW_START",
        "pass": "MUSL_FORK_NOINLINE_RAW_PASS",
    },
    "fork_exec_self": {
        "src": "linux_musl_fork_exec_self.c",
        "start": "MUSL_FORK_EXEC_SELF_START",
        "pass": "MUSL_FORK_EXEC_SELF_PASS",
    },
    "fork_exec_path": {
        "src": "linux_musl_fork_exec_path.c",
        "start": "MUSL_FORK_EXEC_PATH_START",
        "pass": "MUSL_FORK_EXEC_PATH_PASS",
    },
    "fork_child_poweroff": {
        "src": "linux_musl_fork_child_poweroff.c",
        "start": "MUSL_FORK_CHILD_POWEROFF_START",
        "pass": "MUSL_FORK_CHILD_POWEROFF_PASS",
    },
    "printf_string_arg": {
        "src": "linux_musl_printf_string_arg.c",
        "start": "MUSL_PRINTF_STRING_ARG_START",
        "pass": "MUSL_PRINTF_STRING_ARG_PASS",
    },
    "file_stdio": {
        "src": "linux_musl_file_stdio.c",
        "start": "MUSL_FILE_STDIO_START",
        "pass": "MUSL_FILE_STDIO_PASS",
    },
    "time_syscalls": {
        "src": "linux_musl_time_syscalls.c",
        "start": "MUSL_TIME_SYSCALLS_START",
        "pass": "MUSL_TIME_SYSCALLS_PASS",
    },
    "mremap_end": {
        "src": "linux_musl_mremap_end.c",
        "start": "MUSL_MREMAP_END_START",
        "pass": "MUSL_MREMAP_END_PASS",
    },
    "mprotect_adjacent": {
        "src": "linux_musl_mprotect_adjacent.c",
        "start": "MUSL_MPROTECT_ADJACENT_START",
        "pass": "MUSL_MPROTECT_ADJACENT_PASS",
    },
    "tp_preserve": {
        "src": "linux_musl_tp_preserve.c",
        "start": "MUSL_TP_PRESERVE_START",
        "pass": "MUSL_TP_PRESERVE_PASS",
    },
    "cpp17_smoke": {
        "src": "linux_musl_cpp17_smoke.cpp",
        "start": "MUSL_CPP17_START",
        "pass": "MUSL_CPP17_PASS",
    },
    "ebarg_timer": {
        "src": "15_ebarg_init.c",
        "start": "EBARG_INIT_START",
        "pass": "[linx] EBARG selftest: PASS",
    },

}

LIBC_RUNTIME_SAMPLES = [
    "malloc_printf",
    "hello",
    "callret",
    "fork_wait",
    "fork_wait_raw_exit",
    "fork_noinline_raw",
    "fork_exec_self",
    "fork_exec_path",
    "fork_child_poweroff",
    "printf_string_arg",
    "file_stdio",
    "time_syscalls",
    "mremap_end",
    "mprotect_adjacent",
    "tp_preserve",
    "cpp17_smoke",
]

SAMPLE_GROUPS = {
    # Keep the gate-facing "all" group scoped to hosted libc behavior.
    # EBARG is a kernel/interrupt selftest carrier that intentionally spins as
    # PID1 while waiting for a kernel printk, so it must not make libc closure
    # depend on the system timer/EBARG lane.
    "all": LIBC_RUNTIME_SAMPLES,
    "libc-all": LIBC_RUNTIME_SAMPLES,
    "system-all": list(SAMPLES.keys()),
}


def _default_clang() -> Path:
    cands = [
        REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "clang",
        Path("clang"),
    ]
    for p in cands:
        if p.exists():
            return p
    return cands[-1]


def _default_lld() -> Path:
    cands = [
        REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "ld.lld",
        Path("ld.lld"),
    ]
    for p in cands:
        if p.exists():
            return p
    return cands[-1]


def _default_clangxx(clang: Path) -> Path:
    cands = [
        Path(str(clang).replace("/clang", "/clang++")),
        REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "clang++",
        Path("clang++"),
    ]
    for p in cands:
        if p.exists():
            return p
    return cands[-1]


def _default_qemu() -> Path:
    env = os.environ.get("QEMU")
    if env:
        return Path(os.path.expanduser(env))
    cands = [
        REPO_ROOT / "emulator" / "qemu" / "build" / "qemu-system-linx64",
        Path("qemu-system-linx64"),
    ]
    for p in cands:
        if p.exists():
            return p
    return cands[-1]


def _default_qemu_user() -> Path:
    env = os.environ.get("QEMU_USER") or os.environ.get("QEMU_LINX")
    if env:
        return Path(os.path.expanduser(env))
    cands = [
        REPO_ROOT / "emulator" / "qemu" / "build-user" / "qemu-linx",
        REPO_ROOT / "emulator" / "qemu" / "build" / "qemu-linx",
        REPO_ROOT / "emulator" / "qemu" / "linx-linux-user" / "qemu-linx",
        Path("qemu-linx"),
    ]
    for p in cands:
        if p.exists():
            return p
    return cands[-1]


def _check_exe(path: Path, what: str) -> Path:
    # Accept either an absolute/relative path or a PATH-resolved executable name.
    if path.exists():
        if not os.access(path, os.X_OK):
            raise SystemExit(f"error: {what} is not executable: {path}")
        return path

    import shutil

    resolved = shutil.which(str(path))
    if not resolved:
        raise SystemExit(f"error: {what} not found: {path} (and not in PATH)")
    rp = Path(resolved)
    if not os.access(rp, os.X_OK):
        raise SystemExit(f"error: {what} is not executable: {rp}")
    return rp


def _find_kernel(linux_root: Path) -> Path:
    cands = [
        linux_root / "build-linx-fixed" / "vmlinux",
        linux_root / "build-linx" / "vmlinux",
        linux_root / "vmlinux",
    ]
    for p in cands:
        if p.exists():
            return p
    raise SystemExit(f"error: could not find kernel image under {linux_root}")


def _resolve_kernel(linux_root: Path, explicit: str) -> Path:
    kernel = Path(os.path.expanduser(explicit)).resolve() if explicit else _find_kernel(linux_root)
    if not kernel.is_file():
        raise SystemExit(f"error: kernel image not found: {kernel}")
    return kernel


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


def _find_gen_init_cpio(linux_root: Path, out_dir: Path, kernel: Path | None = None) -> Path:
    cands = [
        *(([kernel.parent / "usr" / "gen_init_cpio"]) if kernel is not None else []),
        linux_root / "build-linx-fixed" / "usr" / "gen_init_cpio",
        linux_root / "usr" / "gen_init_cpio",
    ]
    for p in cands:
        if p.exists():
            return p

    src = linux_root / "usr" / "gen_init_cpio.c"
    if not src.exists():
        raise SystemExit(f"error: missing gen_init_cpio source: {src}")

    host_cc = Path("/usr/bin/clang")
    out_bin = out_dir / "gen_init_cpio"
    subprocess.run(
        [str(host_cc), "-O2", "-Wall", "-Wextra", "-o", str(out_bin), str(src)],
        check=True,
    )
    return out_bin


def _find_first_file(cands: list[Path]) -> Path | None:
    for p in cands:
        if p.exists():
            return p
    return None


def _parse_mode_summary(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for ln in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _musl_reuse_errors(
    mode_summary: dict[str, str],
    sysroot: Path,
    runtime_lib: Path,
) -> list[str]:
    errors = [key for key in ("m1", "m2", "m3") if mode_summary.get(key) != "pass"]
    required = [
        sysroot / "lib" / "libc.a",
        sysroot / "lib" / "libc.so",
        sysroot / "lib" / "ld-musl-linx64.so.1",
        runtime_lib,
    ]
    errors.extend(str(path) for path in required if not path.is_file())
    return errors


def _write_summary(path: Path, payload: dict[str, Any]) -> None:
    link_mode = payload.get("link_mode")
    result = payload.get("result")
    mode_results = payload.get("mode_results")
    if isinstance(link_mode, str) and isinstance(result, dict) and isinstance(mode_results, dict):
        mode_results[link_mode] = {
            "ok": bool(result.get("ok", False)),
            "classification": str(result.get("classification", "not_run")),
        }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    if _EXTRA_SUMMARY_PATH and _EXTRA_SUMMARY_PATH != path:
        _EXTRA_SUMMARY_PATH.write_text(text, encoding="utf-8")


def _select_samples(raw_samples: list[str] | None) -> list[str]:
    if not raw_samples:
        return ["malloc_printf"]
    selected: list[str] = []
    for sample in raw_samples:
        selected.extend(SAMPLE_GROUPS.get(sample, [sample]))
    return list(dict.fromkeys(selected))


def _qemu_instruction_failure(text: str) -> tuple[str, str] | None:
    """Return bounded QEMU evidence, preferring the decode-specific message."""
    lines = text.splitlines()
    for classification, marker in (
        ("runtime_qemu_decode_failure", "linx: decode32 failed"),
        ("runtime_qemu_decode_failure", "linx: decode64 failed"),
        ("runtime_qemu_decode_failure", "linx: decode failed"),
        ("runtime_qemu_illegal_instruction", "linx: illegal instruction"),
    ):
        for line in lines:
            if marker in line.lower():
                return classification, line.strip()[:240]
    return None


def _classify_system_runtime_failure(
    text: str,
    *,
    timed_out: bool,
    start_seen: bool,
    pass_seen: bool,
    qemu_rc: int,
    timeout: int,
) -> tuple[str, str] | None:
    if timed_out and start_seen and pass_seen:
        return "runtime_timeout", f"timeout after {timeout}s after pass marker"

    if start_seen and pass_seen:
        if qemu_rc != 0:
            return "runtime_exit_failure", f"pass marker observed with qemu_rc={qemu_rc}"
        if "LINX_REBOOT lisc_shutdown" not in text:
            return (
                "runtime_missing_shutdown",
                "pass marker observed without LINX_REBOOT lisc_shutdown",
            )
        return None

    panic_seen = "Kernel panic - not syncing" in text
    trap_seen = "[linx trap]" in text.lower() or "LINX_USER_TRAP" in text
    timeout_detail = f" (timeout after {timeout}s)" if timed_out else f", qemu_rc={qemu_rc}"
    ordered_guest_failures = (
        (("runtime_block_trap", "linx trap"), ("runtime_kernel_panic", "kernel panic"))
        if timed_out
        else (("runtime_kernel_panic", "kernel panic"), ("runtime_block_trap", "linx trap"))
    )
    if not pass_seen:
        for classification, label in ordered_guest_failures:
            seen = trap_seen if classification == "runtime_block_trap" else panic_seen
            if seen:
                return classification, f"{label} before pass marker{timeout_detail}"

        instruction_failure = _qemu_instruction_failure(text)
        if instruction_failure:
            classification, diagnostic = instruction_failure
            return classification, f"QEMU instruction failure before pass marker: {diagnostic}"

    if timed_out:
        return "runtime_timeout", f"timeout after {timeout}s"

    classification = "runtime_missing_marker"
    if not start_seen:
        classification = "runtime_syscall_failure"
    return (
        classification,
        f"missing markers: start={start_seen} pass={pass_seen}, qemu_rc={qemu_rc}",
    )


def _system_qemu_command(
    qemu: Path,
    kernel: Path,
    initramfs: Path,
    kernel_append: str,
) -> list[str]:
    return [
        str(qemu),
        "-machine",
        "virt",
        "-nographic",
        "-monitor",
        "none",
        "-no-reboot",
        "-d",
        "guest_errors",
        "-kernel",
        str(kernel),
        "-initrd",
        str(initramfs),
        "-append",
        kernel_append,
        "-bios",
        "none",
    ]


def _run_split_link_modes(args: argparse.Namespace, out_dir: Path, selected_samples: list[str]) -> int:
    mode_results: dict[str, Any] = {}
    runner = Path(__file__).resolve()

    for link_mode in ("static", "shared"):
        cmd = [
            sys.executable,
            str(runner),
            "--linux-root",
            args.linux_root,
            "--musl-root",
            args.musl_root,
            "--clang",
            args.clang,
            "--clangxx",
            args.clangxx,
            "--lld",
            args.lld,
            "--qemu",
            args.qemu,
            "--qemu-user",
            args.qemu_user,
            "--target",
            args.target,
            "--image-base",
            args.image_base,
            "--mode",
            args.mode,
            "--link",
            link_mode,
            "--runner",
            args.runner,
            "--callret-crossstack",
            args.callret_crossstack,
            "--timeout",
            str(args.timeout),
            "--out-dir",
            str(out_dir),
        ]
        if args.kernel:
            cmd.extend(["--kernel", args.kernel])
        if args.skip_build:
            cmd.append("--skip-build")
        if args.disable_timer_irq:
            cmd.append("--disable-timer-irq")
        for sample in selected_samples:
            cmd.extend(["--sample", sample])

        run_log = out_dir / f"run_{link_mode}.log"
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        output = proc.stdout.decode("utf-8", errors="replace")
        run_log.write_text(output, encoding="utf-8")

        mode_summary_path = out_dir / f"summary_{link_mode}.json"
        mode_summary: dict[str, Any] = {}
        if mode_summary_path.exists():
            try:
                mode_summary = json.loads(mode_summary_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                mode_summary = {}
        mode_result = mode_summary.get("result", {}) if isinstance(mode_summary, dict) else {}
        mode_ok = bool(mode_result.get("ok", False)) and proc.returncode == 0
        mode_class = str(mode_result.get("classification", "runtime_not_recorded"))
        if proc.returncode != 0 and mode_class == "runtime_pass":
            mode_class = "runtime_subprocess_failure"

        mode_results[link_mode] = {
            "ok": mode_ok,
            "classification": mode_class,
            "exit_code": proc.returncode,
            "summary": str(mode_summary_path),
            "run_log": str(run_log),
            "command": shlex.join(cmd),
            "kernel": (mode_summary.get("paths") or {}).get("kernel", ""),
            "kernel_sha256": mode_summary.get("kernel_sha256", ""),
            "qemu_provenance": mode_summary.get("qemu_provenance", {}),
            "runtime_assets": mode_summary.get("runtime_assets", {}),
        }

    evidence_keys = {
        (
            mode_results[mode]["kernel_sha256"],
            json.dumps(mode_results[mode]["qemu_provenance"], sort_keys=True),
            json.dumps(mode_results[mode]["runtime_assets"], sort_keys=True),
        )
        for mode in ("static", "shared")
    }
    provenance_ok = len(evidence_keys) == 1 and all(
        key[0] and key[1] != "{}" and key[2] != "{}" for key in evidence_keys
    )
    overall_ok = all(mode_results[m]["ok"] for m in ("static", "shared")) and provenance_ok
    summary: dict[str, Any] = {
        "schema_version": "musl-smoke-v2",
        "mode": args.mode,
        "target": args.target,
        "samples": selected_samples,
        "paths": {
            "linux_root": str(Path(os.path.expanduser(args.linux_root)).resolve()),
            "musl_root": str(Path(os.path.expanduser(args.musl_root)).resolve()),
            "clang": str(Path(os.path.expanduser(args.clang)).resolve()),
            "clangxx": str(Path(os.path.expanduser(args.clangxx)).resolve()),
            "lld": str(Path(os.path.expanduser(args.lld)).absolute()),
            "qemu": str(Path(os.path.expanduser(args.qemu)).resolve()),
            "qemu_user": str(Path(os.path.expanduser(args.qemu_user)).resolve()),
            "out_dir": str(out_dir),
            "image_base": args.image_base,
            "link": "both",
            "runner": args.runner,
        },
        "link_modes": ["static", "shared"],
        "mode_results": mode_results,
        "result": {
            "ok": overall_ok,
            "classification": (
                "runtime_pass"
                if overall_ok
                else ("runtime_provenance_mismatch" if not provenance_ok else "runtime_mode_failure")
            ),
        },
    }
    _write_summary(out_dir / "summary.json", summary)

    if overall_ok:
        print(f"ok: musl smoke passed ({out_dir / 'summary.json'})")
        return 0

    print(f"error: musl smoke failed ({out_dir / 'summary.json'})", file=sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run Linx musl malloc/printf runtime smoke on QEMU.")
    parser.add_argument("--linux-root", default=str(REPO_ROOT / "kernel" / "linux"))
    parser.add_argument("--kernel", default="", help="Explicit vmlinux for full-system runtime lanes.")
    parser.add_argument("--musl-root", default=str(REPO_ROOT / "lib" / "musl"))
    parser.add_argument("--clang", default=str(_default_clang()))
    parser.add_argument("--clangxx", default="")
    parser.add_argument("--lld", default=str(_default_lld()))
    parser.add_argument("--qemu", default=str(_default_qemu()))
    parser.add_argument(
        "--qemu-user",
        default=str(_default_qemu_user()),
        help="Linux-user QEMU executable used with --runner user.",
    )
    parser.add_argument("--target", default="linx64-unknown-linux-musl")
    parser.add_argument("--image-base", default="0x40000000")
    parser.add_argument("--mode", choices=["phase-a", "phase-b", "phase-c"], default="phase-b")
    parser.add_argument("--link", choices=["static", "shared", "both"], default="both")
    parser.add_argument(
        "--runner",
        choices=["system", "user"],
        default="system",
        help="Run samples through full-system initramfs QEMU or qemu-linx linux-user mode.",
    )
    parser.add_argument(
        "--callret-crossstack",
        choices=["off", "check", "strict"],
        default="strict",
        help="Cross-stack Linux call/ret audit mode for --sample callret.",
    )
    parser.add_argument(
        "--sample",
        action="append",
        choices=[*SAMPLES.keys(), *SAMPLE_GROUPS.keys()],
        help=(
            "Runtime sample(s) to run (default: malloc_printf). Repeatable. "
            "`all`/`libc-all` select the hosted libc gate group; `system-all` "
            "also includes system probes such as ebarg_timer."
        ),
    )
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Reuse a previously completed musl build after validating its summary and runtime assets.",
    )
    parser.add_argument(
        "--append",
        default="lpj=1000000 loglevel=1 console=ttyS0 kfence.sample_interval=0",
        help="Kernel command line used for QEMU runtime boot.",
    )
    parser.add_argument(
        "--disable-timer-irq",
        action="store_true",
        help="Append `linx_disable_timer_irq=1` to the kernel command line.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(REPO_ROOT / "avs" / "qemu" / "out" / "musl-smoke"),
    )
    args = parser.parse_args(argv)
    disable_timer_irq = args.disable_timer_irq or os.environ.get("LINX_DISABLE_TIMER_IRQ", "").lower() in {
        "1",
        "true",
        "yes",
    }
    if disable_timer_irq and "linx_disable_timer_irq=" not in args.append:
        args.append = f"{args.append} linx_disable_timer_irq=1".strip()

    linux_root = Path(os.path.expanduser(args.linux_root)).resolve()
    musl_root = Path(os.path.expanduser(args.musl_root)).resolve()
    clang = Path(os.path.expanduser(args.clang)).resolve()
    clangxx = (
        Path(os.path.expanduser(args.clangxx)).resolve()
        if args.clangxx
        else _default_clangxx(clang).resolve()
    )
    lld = Path(os.path.expanduser(args.lld)).absolute()
    qemu = Path(os.path.expanduser(args.qemu)).resolve()
    qemu_user = Path(os.path.expanduser(args.qemu_user)).resolve()
    out_dir = Path(os.path.expanduser(args.out_dir)).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    selected_samples = _select_samples(args.sample)
    if args.runner == "user" and "ebarg_timer" in selected_samples:
        raise SystemExit("error: --sample ebarg_timer requires --runner system")
    if "ebarg_timer" in selected_samples and "linx_ebarg_selftest=" not in args.append:
        args.append = f"{args.append} linx_ebarg_selftest=1".strip()
    if "ebarg_timer" in selected_samples and "loglevel=1" in args.append and "loglevel=2" not in args.append:
        args.append = f"{args.append} loglevel=2".strip()
    args.clang = str(clang)
    args.clangxx = str(clangxx)
    args.lld = str(lld)
    args.qemu = str(qemu)
    args.qemu_user = str(qemu_user)
    args.out_dir = str(out_dir)

    if args.link == "both":
        return _run_split_link_modes(args, out_dir, selected_samples)

    global _EXTRA_SUMMARY_PATH
    _EXTRA_SUMMARY_PATH = out_dir / f"summary_{args.link}.json"

    summary: dict[str, Any] = {
        "schema_version": "musl-smoke-v2",
        "mode": args.mode,
        "target": args.target,
        "paths": {
            "linux_root": str(linux_root),
            "musl_root": str(musl_root),
            "clang": str(clang),
            "clangxx": str(clangxx),
            "lld": str(lld),
            "qemu": str(qemu),
            "qemu_user": str(qemu_user),
            "out_dir": str(out_dir),
            "image_base": args.image_base,
            "link": args.link,
            "runner": args.runner,
        },
        "link_mode": args.link,
        "stages": [],
        "result": {"ok": False, "classification": "not_run"},
    }
    summary["samples"] = selected_samples
    summary_path = out_dir / "summary.json"

    def add_stage(name: str, status: str, detail: str, log: str | None = None) -> None:
        item: dict[str, str] = {"name": name, "status": status, "detail": detail}
        if log:
            item["log"] = log
        summary["stages"].append(item)
        _write_summary(summary_path, summary)

    clang = _check_exe(clang, "clang")
    clangxx = _check_exe(clangxx, "clang++")
    lld = _check_exe(lld, "ld.lld")
    if args.runner == "system":
        qemu = _check_exe(qemu, "qemu-system-linx64")
        summary["qemu_provenance"] = qemu_binary_provenance(REPO_ROOT, qemu)
    else:
        qemu_user = _check_exe(qemu_user, "qemu-linx")

    build_script = musl_root / "tools" / "linx" / "build_linx64_musl.sh"
    if not build_script.exists():
        add_stage("musl-build", "fail", f"missing build script: {build_script}")
        summary["result"] = {"ok": False, "classification": "musl_build_script_missing"}
        _write_summary(summary_path, summary)
        return 2

    sysroot = REPO_ROOT / "out" / "libc" / "musl" / "install" / args.mode
    runtime_lib = REPO_ROOT / "out" / "libc" / "musl" / "runtime" / args.mode / "liblinx_builtin_rt.a"
    build_log = out_dir / "musl_build.log"
    env = os.environ.copy()
    env["MODE"] = args.mode
    env["TARGET"] = args.target
    env["LINX_ISA_ROOT"] = str(REPO_ROOT)
    env["CLANG"] = str(clang)
    llvm_bin = clang.parent
    env["LLVM_BIN"] = str(llvm_bin)
    env["AR"] = str(llvm_bin / "llvm-ar")
    env["RANLIB"] = str(llvm_bin / "llvm-ranlib")
    env["NM"] = str(llvm_bin / "llvm-nm")
    env["STRIP"] = str(llvm_bin / "llvm-strip")
    env["READELF"] = str(llvm_bin / "llvm-readelf")

    mode_summary = _parse_mode_summary(REPO_ROOT / "out" / "libc" / "musl" / "logs" / f"{args.mode}-summary.txt")
    if args.skip_build:
        reuse_errors = _musl_reuse_errors(mode_summary, sysroot, runtime_lib)
        if reuse_errors:
            add_stage("musl-build", "fail", "invalid reusable musl build: " + ", ".join(reuse_errors))
            summary["result"] = {"ok": False, "classification": "musl_reuse_validation_failure"}
            _write_summary(summary_path, summary)
            return 2
        add_stage("musl-build", "pass", "reused validated m1/m2/m3 outputs")
    else:
        with build_log.open("w", encoding="utf-8") as fp:
            fp.write("+ " + shlex.join([str(build_script)]) + "\n")
            rc = subprocess.run(
                [str(build_script)],
                cwd=str(musl_root),
                env=env,
                stdout=fp,
                stderr=subprocess.STDOUT,
                check=False,
            ).returncode
        mode_summary = _parse_mode_summary(REPO_ROOT / "out" / "libc" / "musl" / "logs" / f"{args.mode}-summary.txt")
        if rc != 0:
            classification = "musl_build_failure"
            if mode_summary.get("m1") == "fail":
                classification = "musl_configure_failure"
            elif mode_summary.get("m2") == "fail":
                classification = "musl_static_lib_failure"
            add_stage("musl-build", "fail", f"musl build failed (mode={args.mode})", str(build_log))
            summary["result"] = {"ok": False, "classification": classification}
            _write_summary(summary_path, summary)
            return 2
        add_stage("musl-build", "pass", f"m1={mode_summary.get('m1', 'unknown')} m2={mode_summary.get('m2', 'unknown')} m3={mode_summary.get('m3', 'unknown')}", str(build_log))
    reusable_assets = {
        "libc.a": sysroot / "lib" / "libc.a",
        "libc.so": sysroot / "lib" / "libc.so",
        "loader": sysroot / "lib" / "ld-musl-linx64.so.1",
        "runtime_builtins": runtime_lib,
    }
    summary["runtime_assets"] = {
        name: _file_evidence(path)
        for name, path in reusable_assets.items()
        if path.is_file()
    }
    env_compile = os.environ.copy()
    env_compile["PATH"] = f"{lld.parent}:{env_compile.get('PATH', '')}"
    if args.runner == "system":
        kernel = _resolve_kernel(linux_root, args.kernel)
        gen_init_cpio = _find_gen_init_cpio(linux_root, out_dir, kernel)
        summary["paths"]["kernel"] = str(kernel)
        summary["kernel_sha256"] = _sha256(kernel)
        _write_summary(summary_path, summary)

    if args.link == "both":
        link_modes = ["static", "shared"]
    else:
        link_modes = [args.link]
    summary["link_modes"] = link_modes
    summary["mode_results"] = {args.link: {"ok": False, "classification": "not_run"}}

    if "callret" in selected_samples and args.callret_crossstack != "off":
        audit_script = REPO_ROOT / "tools" / "ci" / "check_linx_callret_crossstack.sh"
        if not audit_script.exists():
            add_stage("callret-crossstack", "fail", f"missing audit script: {audit_script}")
            summary["result"] = {"ok": False, "classification": "callret_crossstack_script_missing"}
            _write_summary(summary_path, summary)
            return 2

        audit_log = out_dir / "callret_crossstack.log"
        audit_env = os.environ.copy()
        # Whole-vmlinux disassembly audit is expensive and can be enabled
        # explicitly when needed; keep object-level contract checks on by default.
        audit_env["LINX_AUDIT_VMLINUX"] = os.environ.get("LINX_AUDIT_VMLINUX", "0")
        if args.callret_crossstack == "strict":
            audit_env["LINX_STRICT_CALLRET_RELOCS"] = "1"

        with audit_log.open("w", encoding="utf-8") as fp:
            cmd = [str(audit_script), str(linux_root)]
            fp.write("+ " + shlex.join(cmd) + "\n")
            rc = subprocess.run(
                cmd,
                env=audit_env,
                stdout=fp,
                stderr=subprocess.STDOUT,
                check=False,
            ).returncode
        if rc != 0:
            add_stage(
                "callret-crossstack",
                "fail",
                f"linux call/ret cross-stack audit failed (mode={args.callret_crossstack})",
                str(audit_log),
            )
            summary["result"] = {
                "ok": False,
                "classification": "callret_linux_crossstack_contract_failure",
            }
            _write_summary(summary_path, summary)
            return 2
        add_stage(
            "callret-crossstack",
            "pass",
            f"linux call/ret cross-stack audit passed (mode={args.callret_crossstack})",
            str(audit_log),
        )

    if not runtime_lib.exists():
        add_stage("sample-compile", "fail", f"missing runtime builtins archive: {runtime_lib}")
        summary["result"] = {"ok": False, "classification": "runtime_builtins_missing"}
        _write_summary(summary_path, summary)
        return 2

    for sample_name in selected_samples:
        sample_meta = SAMPLES[sample_name]
        sample_src = SCRIPT_DIR / "tests" / sample_meta["src"]
        if not sample_src.exists():
            add_stage("sample-compile", "fail", f"missing sample source: {sample_src}")
            summary["result"] = {"ok": False, "classification": f"{sample_name}_source_missing"}
            _write_summary(summary_path, summary)
            return 2

        for link_mode in link_modes:
            sample_bin = out_dir / f"{sample_name}_{link_mode}"
            sample_obj = out_dir / f"{sample_src.stem}_{link_mode}.o"
            compile_log = out_dir / f"compile_{sample_name}_{link_mode}.log"
            is_cpp = sample_src.suffix in {".cc", ".cpp", ".cxx"}
            compile_tool = clangxx if is_cpp else clang

            shared_lib = sysroot / "lib" / "libc.so"
            shared_loader = sysroot / "lib" / "ld-musl-linx64.so.1"
            lib_search = [
                sysroot / "lib",
                sysroot / "usr/lib",
                REPO_ROOT / "out" / "cpp-runtime" / "musl-cxx17-noeh" / "install" / "lib",
                REPO_ROOT / "out" / "cpp-runtime" / "musl-cxx17-noeh" / "install" / "usr/lib",
            ]
            cpp_static_libs: list[str] = []
            cpp_unwindlib = "none"
            cpp_include_dir: Path | None = None
            if is_cpp:
                libcxx = _find_first_file([d / "libc++.a" for d in lib_search])
                libcxxabi = _find_first_file([d / "libc++abi.a" for d in lib_search])
                libunwind = _find_first_file([d / "libunwind.a" for d in lib_search])
                if libcxx is None or libcxxabi is None:
                    add_stage(
                        f"sample-compile[{sample_name}:{link_mode}]",
                        "fail",
                        "missing static C++ runtime archives (libc++, libc++abi)",
                    )
                    summary["result"] = {
                        "ok": False,
                        "classification": f"{sample_name}_{link_mode}_cpp_runtime_lib_missing",
                    }
                    _write_summary(summary_path, summary)
                    return 2
                cpp_static_libs = [str(libcxx), str(libcxxabi)]
                if libunwind is not None:
                    cpp_static_libs.append(str(libunwind))
                    cpp_unwindlib = "libunwind"
                cpp_include_dir = _find_first_file(
                    [
                        sysroot / "include" / "c++" / "v1",
                        sysroot / "usr" / "include" / "c++" / "v1",
                        REPO_ROOT
                        / "out"
                        / "cpp-runtime"
                        / "musl-cxx17-noeh"
                        / "install"
                        / "include"
                        / "c++"
                        / "v1",
                    ]
                )
                if cpp_include_dir is None:
                    add_stage(
                        f"sample-compile[{sample_name}:{link_mode}]",
                        "fail",
                        "missing C++ headers (c++/v1) in sysroot/runtime overlay",
                    )
                    summary["result"] = {
                        "ok": False,
                        "classification": f"{sample_name}_{link_mode}_cpp_headers_missing",
                    }
                    _write_summary(summary_path, summary)
                    return 2

            compile_sample_cmd = [
                str(compile_tool),
                "-target",
                args.target,
                "--sysroot",
                str(sysroot),
            ]
            if is_cpp:
                compile_sample_cmd += [
                    "-std=c++17",
                    "-fno-exceptions",
                    "-fno-rtti",
                    "-nostdinc++",
                    "-isystem",
                    str(cpp_include_dir),
                    "-stdlib=libc++",
                    "-rtlib=compiler-rt",
                    "-unwindlib=" + cpp_unwindlib,
                ]
            compile_sample_cmd += [
                # Linx Linux bring-up runs NOMMU/FDPIC; user binaries must be PIE (ET_DYN).
                "-fPIE",
                "-c",
                str(sample_src),
                "-o",
                str(sample_obj),
            ]

            # When we link PIE (-pie) we must use the matching startup object:
            # - `rcrt1.o` for static PIE (self-relocating crt1; fills RELATIVE relocations)
            # - `Scrt1.o` for dynamic/PIE
            # Fall back to `crt1.o` only if the preferred object is unavailable.
            crt1_order = (
                ["rcrt1.o", "crt1.o", "Scrt1.o"]
                if link_mode == "static"
                else ["Scrt1.o", "crt1.o", "rcrt1.o"]
            )
            crt1_obj = _find_first_file([sysroot / "lib" / n for n in crt1_order])
            if crt1_obj is None:
                add_stage(
                    f"sample-compile[{sample_name}:{link_mode}]",
                    "fail",
                    "missing startup CRT object (crt1/Scrt1/rcrt1)",
                )
                summary["result"] = {
                    "ok": False,
                    "classification": f"{sample_name}_{link_mode}_crt_startup_missing",
                }
                _write_summary(summary_path, summary)
                return 2

            if link_mode == "static":
                if is_cpp:
                    link_cmd = [
                        str(clangxx),
                        "-target",
                        args.target,
                        "--sysroot",
                        str(sysroot),
                        "-std=c++17",
                        "-fno-exceptions",
                        "-fno-rtti",
                        "-static",
                        "-Wl,-pie",
                        "-unwindlib=" + cpp_unwindlib,
                        "-fuse-ld=lld",
                        "-nostdlib",
                        str(crt1_obj),
                        str(sysroot / "lib" / "crti.o"),
                        str(sample_obj),
                        str(runtime_lib),
                        *cpp_static_libs,
                        str(sysroot / "lib" / "libc.a"),
                        str(sysroot / "lib" / "crtn.o"),
                        f"-Wl,--image-base={args.image_base}",
                        "-o",
                        str(sample_bin),
                    ]
                else:
                    link_cmd = [
                        str(clang),
                        "-target",
                        args.target,
                        "--sysroot",
                        str(sysroot),
                        "-static",
                        "-Wl,-pie",
                        "-fuse-ld=lld",
                        "-nostdlib",
                        str(crt1_obj),
                        str(sysroot / "lib" / "crti.o"),
                        str(sample_obj),
                        str(runtime_lib),
                        str(sysroot / "lib" / "libc.a"),
                        str(sysroot / "lib" / "crtn.o"),
                        f"-Wl,--image-base={args.image_base}",
                        "-o",
                        str(sample_bin),
                    ]
            else:
                if not shared_lib.exists() or not shared_loader.exists():
                    add_stage(
                        f"sample-compile[{sample_name}:{link_mode}]",
                        "fail",
                        f"missing shared runtime artifacts: {shared_lib} / {shared_loader}",
                    )
                    summary["result"] = {
                        "ok": False,
                        "classification": f"{sample_name}_{link_mode}_runtime_artifacts_missing",
                    }
                    _write_summary(summary_path, summary)
                    return 2
                if is_cpp:
                    link_cmd = [
                        str(clangxx),
                        "-target",
                        args.target,
                        "--sysroot",
                        str(sysroot),
                        "-std=c++17",
                        "-fno-exceptions",
                        "-fno-rtti",
                        "-Wl,-pie",
                        "-unwindlib=" + cpp_unwindlib,
                        "-fuse-ld=lld",
                        "-nostdlib",
                        str(crt1_obj),
                        str(sysroot / "lib" / "crti.o"),
                        str(sample_obj),
                        str(runtime_lib),
                        *cpp_static_libs,
                        "-L" + str(sysroot / "lib"),
                        "-L" + str(sysroot / "usr/lib"),
                        "-lc",
                        str(sysroot / "lib" / "crtn.o"),
                        "-Wl,--dynamic-linker=/lib/ld-musl-linx64.so.1",
                        f"-Wl,--image-base={args.image_base}",
                        "-o",
                        str(sample_bin),
                    ]
                else:
                    link_cmd = [
                        str(clang),
                        "-target",
                        args.target,
                        "--sysroot",
                        str(sysroot),
                        "-Wl,-pie",
                        "-fuse-ld=lld",
                        "-nostdlib",
                        str(crt1_obj),
                        str(sysroot / "lib" / "crti.o"),
                        str(sample_obj),
                        str(runtime_lib),
                        "-L" + str(sysroot / "lib"),
                        "-L" + str(sysroot / "usr/lib"),
                        "-lc",
                        str(sysroot / "lib" / "crtn.o"),
                        "-Wl,--dynamic-linker=/lib/ld-musl-linx64.so.1",
                        f"-Wl,--image-base={args.image_base}",
                        "-o",
                        str(sample_bin),
                    ]

            with compile_log.open("w", encoding="utf-8") as fp:
                rc = 0
                for cmd in [compile_sample_cmd, link_cmd]:
                    fp.write("+ " + shlex.join(cmd) + "\n")
                    rc = subprocess.run(
                        cmd,
                        env=env_compile,
                        stdout=fp,
                        stderr=subprocess.STDOUT,
                        check=False,
                    ).returncode
                    if rc != 0:
                        break
            if rc != 0:
                add_stage(
                    f"sample-compile[{sample_name}:{link_mode}]",
                    "fail",
                    "failed to compile/link musl sample",
                    str(compile_log),
                )
                summary["result"] = {
                    "ok": False,
                    "classification": f"{sample_name}_{link_mode}_sample_compile_failure",
                }
                _write_summary(summary_path, summary)
                return 2
            add_stage(
                f"sample-compile[{sample_name}:{link_mode}]",
                "pass",
                f"built {sample_bin}",
                str(compile_log),
            )

            if args.runner == "user":
                qemu_log = out_dir / f"qemu_user_{sample_name}_{link_mode}.log"
                qemu_cmd = [
                    str(qemu_user),
                    "-L",
                    str(sysroot),
                    str(sample_bin),
                ]

                text = ""
                qemu_rc = 124
                timed_out = False
                try:
                    proc = subprocess.run(
                        qemu_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        timeout=args.timeout,
                        check=False,
                    )
                    qemu_rc = proc.returncode
                    text = proc.stdout.decode("utf-8", errors="replace")
                except subprocess.TimeoutExpired as exc:
                    timed_out = True
                    data = exc.output if isinstance(exc.output, (bytes, bytearray)) else b""
                    text = data.decode("utf-8", errors="replace")

                qemu_log.write_text(text, encoding="utf-8")

                start_seen = sample_meta["start"] in text
                pass_seen = sample_meta["pass"] in text
                if timed_out:
                    add_stage(
                        f"qemu-user-runtime[{sample_name}:{link_mode}]",
                        "fail",
                        f"timeout after {args.timeout}s",
                        str(qemu_log),
                    )
                    summary["result"] = {
                        "ok": False,
                        "classification": f"{sample_name}_{link_mode}_user_runtime_timeout",
                    }
                    _write_summary(summary_path, summary)
                    return 2
                if qemu_rc != 0:
                    add_stage(
                        f"qemu-user-runtime[{sample_name}:{link_mode}]",
                        "fail",
                        f"nonzero qemu/user exit code {qemu_rc}",
                        str(qemu_log),
                    )
                    summary["result"] = {
                        "ok": False,
                        "classification": f"{sample_name}_{link_mode}_user_runtime_exit_failure",
                    }
                    _write_summary(summary_path, summary)
                    return 2
                if not start_seen or not pass_seen:
                    classification = f"{sample_name}_{link_mode}_user_runtime_missing_marker"
                    if not start_seen:
                        classification = f"{sample_name}_{link_mode}_user_runtime_syscall_failure"
                    add_stage(
                        f"qemu-user-runtime[{sample_name}:{link_mode}]",
                        "fail",
                        f"missing markers: start={start_seen} pass={pass_seen}, qemu_rc={qemu_rc}",
                        str(qemu_log),
                    )
                    summary["result"] = {"ok": False, "classification": classification}
                    _write_summary(summary_path, summary)
                    return 2

                add_stage(
                    f"qemu-user-runtime[{sample_name}:{link_mode}]",
                    "pass",
                    f"markers observed; qemu_rc={qemu_rc}",
                    str(qemu_log),
                )
                continue

            initramfs_list = out_dir / f"initramfs_{sample_name}_{link_mode}.list"
            initramfs = out_dir / f"initramfs_{sample_name}_{link_mode}.cpio"
            initramfs_log = out_dir / f"initramfs_{sample_name}_{link_mode}.log"

            init_lines = [
                "dir /dev 0755 0 0",
                "nod /dev/console 0600 0 0 c 5 1",
                "nod /dev/null 0666 0 0 c 1 3",
                "nod /dev/ttyS0 0600 0 0 c 4 64",
                "dir /proc 0755 0 0",
                "dir /sys 0755 0 0",
                "dir /run 0755 0 0",
                "dir /tmp 1777 0 0",
                f"file /init {sample_bin} 0755 0 0",
            ]
            if sample_name == "fork_exec_path":
                init_lines.append(f"file /child_exec_path {sample_bin} 0755 0 0")
            if link_mode == "shared":
                loader_src = shared_loader if shared_loader.exists() else shared_lib
                init_lines += [
                    "dir /lib 0755 0 0",
                    f"file /lib/libc.so {shared_lib} 0755 0 0",
                    f"file /lib/ld-musl-linx64.so.1 {loader_src} 0755 0 0",
                ]
            init_lines.append("")
            initramfs_list.write_text("\n".join(init_lines), encoding="utf-8")

            cmd_gen = [str(gen_init_cpio), "-o", str(initramfs), str(initramfs_list)]
            with initramfs_log.open("w", encoding="utf-8") as fp:
                fp.write("+ " + shlex.join(cmd_gen) + "\n")
                rc = subprocess.run(cmd_gen, stdout=fp, stderr=subprocess.STDOUT, check=False).returncode
            if rc != 0:
                add_stage(
                    f"initramfs[{sample_name}:{link_mode}]",
                    "fail",
                    "failed to create initramfs",
                    str(initramfs_log),
                )
                summary["result"] = {
                    "ok": False,
                    "classification": f"{sample_name}_{link_mode}_initramfs_generation_failure",
                }
                _write_summary(summary_path, summary)
                return 2
            add_stage(
                f"initramfs[{sample_name}:{link_mode}]",
                "pass",
                f"built {initramfs}",
                str(initramfs_log),
            )

            qemu_log = out_dir / f"qemu_{sample_name}_{link_mode}.log"
            qemu_cmd = _system_qemu_command(qemu, kernel, initramfs, args.append)

            text = ""
            qemu_rc = 124
            timed_out = False
            try:
                proc = subprocess.run(
                    qemu_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=args.timeout,
                    check=False,
                )
                qemu_rc = proc.returncode
                text = proc.stdout.decode("utf-8", errors="replace")
            except subprocess.TimeoutExpired as exc:
                timed_out = True
                data = exc.output if isinstance(exc.output, (bytes, bytearray)) else b""
                text = data.decode("utf-8", errors="replace")

            qemu_log.write_text(text, encoding="utf-8")

            start_seen = sample_meta["start"] in text
            pass_seen = sample_meta["pass"] in text
            runtime_failure = _classify_system_runtime_failure(
                text,
                timed_out=timed_out,
                start_seen=start_seen,
                pass_seen=pass_seen,
                qemu_rc=qemu_rc,
                timeout=args.timeout,
            )
            if runtime_failure:
                classification, detail = runtime_failure
                add_stage(
                    f"qemu-runtime[{sample_name}:{link_mode}]",
                    "fail",
                    detail,
                    str(qemu_log),
                )
                summary["result"] = {
                    "ok": False,
                    "classification": f"{sample_name}_{link_mode}_{classification}",
                }
                _write_summary(summary_path, summary)
                return 2

            add_stage(
                f"qemu-runtime[{sample_name}:{link_mode}]",
                "pass",
                f"markers observed; qemu_rc={qemu_rc}",
                str(qemu_log),
            )

    summary["result"] = {"ok": True, "classification": "runtime_pass"}
    _write_summary(summary_path, summary)
    print(f"ok: musl smoke passed ({summary_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
