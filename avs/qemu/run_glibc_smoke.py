#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

HELLO_VARIANTS: dict[str, str] = {
    "entry_main": "hello_glibc_entry_main",
    "shared": "hello_glibc_shared",
    "startup": "hello_glibc_startup",
    "startup_norpath": "hello_glibc_startup_norpath",
}

PASS_MARKERS = [
    "WRAP_INIT_START",
    "GLIBC_HELLO_START",
    "Hello, Linx ISA Linux via QEMU (glibc)",
    "GLIBC_HELLO_PASS",
]

FAIL_MARKERS = [
    "WRAP_INIT_EXECVE_FAIL",
    "error while loading shared libraries:",
    "Kernel panic - not syncing:",
]


def _default_qemu() -> Path:
    cands = [
        REPO_ROOT / "emulator" / "qemu" / "build" / "qemu-system-linx64",
        Path("qemu-system-linx64"),
    ]
    for p in cands:
        if p.exists():
            return p
    return cands[-1]


def _check_exe(path: Path, what: str) -> Path:
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


def _find_gen_init_cpio(linux_root: Path, out_dir: Path) -> Path:
    cands = [
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


def _write_summary(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_qemu(cmd: list[str], timeout_s: int) -> tuple[str, bool, bool]:
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    timed_out = False
    saw_pass = False
    out_chunks: list[bytes] = []
    deadline = time.monotonic() + timeout_s

    while True:
        now = time.monotonic()
        if now >= deadline:
            timed_out = True
            proc.kill()
            break

        wait_s = min(0.25, max(0.0, deadline - now))
        r, _, _ = select.select([proc.stdout], [], [], wait_s)
        if r:
            chunk = os.read(proc.stdout.fileno(), 4096)
            if not chunk:
                break
            out_chunks.append(chunk)
            text = b"".join(out_chunks).decode("utf-8", errors="replace")
            if all(marker in text for marker in PASS_MARKERS):
                saw_pass = True
                proc.kill()
                break
            if any(marker in text for marker in FAIL_MARKERS):
                proc.kill()
                break

        if proc.poll() is not None:
            break

    if proc.poll() is None:
        proc.kill()
    tail_out = proc.stdout.read() if proc.stdout else b""
    if tail_out:
        out_chunks.append(tail_out)
    return b"".join(out_chunks).decode("utf-8", errors="replace"), timed_out, saw_pass


def _select_variants(raw: list[str] | None) -> list[str]:
    if not raw:
        return list(HELLO_VARIANTS.keys())
    if "all" in raw:
        return list(HELLO_VARIANTS.keys())
    ordered = list(dict.fromkeys(raw))
    unknown = [item for item in ordered if item not in HELLO_VARIANTS]
    if unknown:
        raise SystemExit(f"error: unknown --variant value(s): {', '.join(unknown)}")
    return ordered


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run the glibc dynamic-runtime hello matrix on Linux+QEMU.")
    parser.add_argument("--linux-root", default=str(REPO_ROOT / "kernel" / "linux"))
    parser.add_argument("--glibc-build", default=str(REPO_ROOT / "out" / "libc" / "glibc" / "build"))
    parser.add_argument("--clang", default=str(REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "clang"))
    parser.add_argument("--qemu", default=str(_default_qemu()))
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument(
        "--append",
        default="lpj=1000000 loglevel=1 console=ttyS0 panic=-1",
        help="Kernel command line used for QEMU runtime boot.",
    )
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "avs" / "qemu" / "out" / "glibc-smoke"))
    parser.add_argument("--wrapper", default="")
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Reuse existing glibc hello artifacts instead of rebuilding them first.",
    )
    parser.add_argument(
        "--variant",
        action="append",
        choices=[*HELLO_VARIANTS.keys(), "all"],
        help="Hello binary variant(s) to run. Repeatable. Default: all known glibc runtime variants.",
    )
    parser.add_argument(
        "--hello",
        default="",
        help="Override the hello binary path for single-variant ad hoc repros.",
    )
    args = parser.parse_args(argv)

    linux_root = Path(os.path.expanduser(args.linux_root)).resolve()
    glibc_build = Path(os.path.expanduser(args.glibc_build)).resolve()
    clang = _check_exe(Path(os.path.expanduser(args.clang)), "clang")
    qemu = _check_exe(Path(os.path.expanduser(args.qemu)), "qemu-system-linx64")
    out_dir = Path(os.path.expanduser(args.out_dir)).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "summary.json"
    summary: dict[str, Any] = {
        "schema_version": "glibc-runtime-v2",
        "paths": {
            "linux_root": str(linux_root),
            "glibc_build": str(glibc_build),
            "clang": str(clang),
            "qemu": str(qemu),
            "out_dir": str(out_dir),
        },
        "stages": [],
        "result": {"ok": False, "classification": "not_run"},
    }

    def add_stage(name: str, status: str, detail: str, log: str | None = None) -> None:
        item: dict[str, str] = {"name": name, "status": status, "detail": detail}
        if log:
            item["log"] = log
        summary["stages"].append(item)
        _write_summary(summary_path, summary)

    kernel = _find_kernel(linux_root)
    gen_init_cpio = _find_gen_init_cpio(linux_root, out_dir)
    wrapper = (
        Path(os.path.expanduser(args.wrapper)).resolve()
        if args.wrapper
        else (out_dir / "wrap_init_musl_staticpie_env")
    )
    ldso = glibc_build / "elf" / "ld.so.1"
    libc = glibc_build / "libc.so"
    selected_variants = _select_variants(args.variant)
    if args.hello:
        selected_variants = ["custom"]
        hello_paths = {"custom": Path(os.path.expanduser(args.hello)).resolve()}
    else:
        if not args.skip_build:
            build_script = SCRIPT_DIR / "build_glibc_smoke.py"
            subprocess.run(
                [
                    str(build_script),
                    "--clang",
                    str(clang),
                    "--glibc-build",
                    str(glibc_build),
                    "--out-dir",
                    str(out_dir),
                ],
                check=True,
            )
        hello_paths = {variant: out_dir / HELLO_VARIANTS[variant] for variant in selected_variants}

    required_files = {
        "wrapper": wrapper,
        "ld.so.1": ldso,
        "libc.so.6": libc,
        "kernel": kernel,
        "gen_init_cpio": gen_init_cpio,
    }
    for variant, hello_path in hello_paths.items():
        required_files[f"hello[{variant}]"] = hello_path
    missing = [f"{name}={path}" for name, path in required_files.items() if not path.exists()]
    if missing:
        add_stage("asset-check", "fail", "missing required runtime asset(s): " + ", ".join(missing))
        summary["result"] = {"ok": False, "classification": "glibc_runtime_asset_missing"}
        _write_summary(summary_path, summary)
        return 2

    add_stage(
        "asset-check",
        "pass",
        f"wrapper, {len(hello_paths)} hello variant(s), loader, libc, and kernel assets are present",
    )

    variant_results: dict[str, Any] = {}
    overall_ok = True
    for variant in selected_variants:
        hello = hello_paths[variant]
        initramfs_list = out_dir / f"initramfs_glibc_runtime_{variant}.list"
        initramfs_cpio = out_dir / f"initramfs_glibc_runtime_{variant}.cpio"
        initramfs_list.write_text(
            "\n".join(
                [
                    "dir /dev 0755 0 0",
                    "nod /dev/console 0600 0 0 c 5 1",
                    "nod /dev/null 0666 0 0 c 1 3",
                    "nod /dev/ttyS0 0600 0 0 c 4 64",
                    "dir /proc 0755 0 0",
                    "dir /sys 0755 0 0",
                    "dir /run 0755 0 0",
                    "dir /tmp 1777 0 0",
                    "dir /lib 0755 0 0",
                    f"file /init {wrapper} 0755 0 0",
                    f"file /hello {hello} 0755 0 0",
                    f"file /lib/ld.so.1 {ldso} 0755 0 0",
                    f"file /lib/libc.so.6 {libc} 0755 0 0",
                    "slink /lib/libc.so /lib/libc.so.6 0755 0 0",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        with initramfs_cpio.open("wb") as fp:
            rc = subprocess.run(
                [str(gen_init_cpio), str(initramfs_list)],
                stdout=fp,
                stderr=subprocess.PIPE,
                check=False,
            )
        if rc.returncode != 0:
            detail = f"gen_init_cpio failed with rc={rc.returncode}: {rc.stderr.decode('utf-8', errors='replace').strip()}"
            add_stage(f"initramfs-build[{variant}]", "fail", detail, str(initramfs_list))
            summary["result"] = {"ok": False, "classification": "glibc_runtime_initramfs_failure"}
            _write_summary(summary_path, summary)
            return 2
        add_stage(f"initramfs-build[{variant}]", "pass", f"built {initramfs_cpio}", str(initramfs_list))

        qemu_log = out_dir / f"qemu_glibc_runtime_{variant}.log"
        cmd = [
            str(qemu),
            "-nographic",
            "-monitor",
            "none",
            "-machine",
            "virt",
            "-m",
            "512M",
            "-smp",
            "1",
            "-kernel",
            str(kernel),
            "-initrd",
            str(initramfs_cpio),
            "-append",
            args.append,
        ]
        output, timed_out, saw_pass = _run_qemu(cmd, args.timeout)
        qemu_log.write_text(output, encoding="utf-8")
        missing_markers = [marker for marker in PASS_MARKERS if marker not in output]

        if saw_pass and not missing_markers:
            detail = "glibc-linked hello reached main and reported pass"
            classification = "runtime_pass"
            ok = True
            add_stage(f"qemu-runtime[{variant}]", "pass", detail, str(qemu_log))
        else:
            ok = False
            overall_ok = False
            if timed_out:
                detail = f"qemu timed out after {args.timeout}s"
                classification = "glibc_runtime_timeout"
            elif any(marker in output for marker in FAIL_MARKERS):
                hit = next(marker for marker in FAIL_MARKERS if marker in output)
                detail = f"runtime hit failure marker: {hit}"
                classification = "glibc_runtime_failure_marker"
            else:
                detail = "missing pass markers: " + ", ".join(missing_markers)
                classification = "glibc_runtime_missing_marker"
            add_stage(f"qemu-runtime[{variant}]", "fail", detail, str(qemu_log))

        variant_results[variant] = {
            "hello": str(hello),
            "initramfs": str(initramfs_cpio),
            "log": str(qemu_log),
            "ok": ok,
            "classification": classification,
        }

    summary["variants"] = variant_results
    summary["result"] = {
        "ok": overall_ok,
        "classification": "runtime_pass" if overall_ok else "glibc_runtime_variant_failure",
    }
    _write_summary(summary_path, summary)

    if overall_ok:
        print(f"ok: glibc runtime matrix passed ({summary_path})")
        return 0

    print(f"error: glibc runtime matrix failed ({summary_path})", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
