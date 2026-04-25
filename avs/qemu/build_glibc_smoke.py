#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]


def _default_clang() -> Path:
    cands = [
        REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "clang",
        Path("clang"),
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


def _run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Build reproducible glibc hello runtime artifacts for Linux+QEMU.")
    parser.add_argument("--clang", default=str(_default_clang()))
    parser.add_argument("--glibc-build", default=str(REPO_ROOT / "out" / "libc" / "glibc" / "build"))
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "avs" / "qemu" / "out" / "glibc-smoke"))
    args = parser.parse_args(argv)

    clang = _check_exe(Path(os.path.expanduser(args.clang)), "clang")
    glibc_build = Path(os.path.expanduser(args.glibc_build)).resolve()
    out_dir = Path(os.path.expanduser(args.out_dir)).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    src = REPO_ROOT / "avs" / "qemu" / "tests" / "linux_glibc_hello_min.c"
    if not src.exists():
        raise SystemExit(f"error: missing source: {src}")
    wrapper_src = REPO_ROOT / "avs" / "qemu" / "tests" / "wrap_init_musl_staticpie_env.c"
    if not wrapper_src.exists():
        raise SystemExit(f"error: missing source: {wrapper_src}")

    required = {
        "crt1.o": glibc_build / "csu" / "crt1.o",
        "Scrt1.o": glibc_build / "csu" / "Scrt1.o",
        "crti.o": glibc_build / "csu" / "crti.o",
        "crtn.o": glibc_build / "csu" / "crtn.o",
        "libc.so": glibc_build / "libc.so",
    }
    missing = [f"{name}={path}" for name, path in required.items() if not path.exists()]
    if missing:
        raise SystemExit("error: missing glibc build artifact(s): " + ", ".join(missing))

    common = [
        str(clang),
        "--target=linx64-unknown-linux-gnu",
        "-fuse-ld=lld",
        "-O2",
        "-g",
        "-fPIE",
        "-pie",
        "-Wl,-dynamic-linker,/lib/ld.so.1",
        "-nostdlib",
    ]

    obj = out_dir / "linux_glibc_hello_shared.o"
    _run(
        [
            str(clang),
            "--target=linx64-unknown-linux-gnu",
            "-O2",
            "-g",
            "-fPIC",
            "-c",
            str(src),
            "-o",
            str(obj),
        ]
    )

    wrapper_common = [
        str(clang),
        "--target=linx64-unknown-linux-gnu",
        "-Oz",
        "-g",
        "-ffreestanding",
        "-fno-builtin",
        "-fpie",
        "-fpic",
        "-fno-stack-protector",
        "-fno-asynchronous-unwind-tables",
        "-fno-unwind-tables",
        "-nostdlib",
        "-static",
        "-fuse-ld=lld",
        "-Wl,-pie",
        "-Wl,-e,_start",
        "-Wl,--build-id=none",
    ]
    _run(
        wrapper_common
        + [
            str(wrapper_src),
            "-o",
            str(out_dir / "wrap_init_musl_staticpie_env"),
        ]
    )

    # Direct-entry executable for minimum rtld handoff coverage.
    _run(
        common
        + [
            "-Wl,-e,main",
            str(src),
            str(glibc_build / "libc.so"),
            "-o",
            str(out_dir / "hello_glibc_entry_main"),
        ]
    )

    # Standard dynamic executable using crt1 startup.
    _run(
        common
        + [
            str(glibc_build / "csu" / "crti.o"),
            str(glibc_build / "csu" / "crt1.o"),
            str(src),
            str(glibc_build / "libc.so"),
            str(glibc_build / "csu" / "crtn.o"),
            "-o",
            str(out_dir / "hello_glibc_shared"),
        ]
    )

    # PIE startup with explicit runpath to mirror the original startup artifact.
    _run(
        common
        + [
            str(glibc_build / "csu" / "crti.o"),
            str(glibc_build / "csu" / "Scrt1.o"),
            str(src),
            str(glibc_build / "libc.so"),
            str(glibc_build / "csu" / "crtn.o"),
            "-Wl,-rpath,/lib",
            "-o",
            str(out_dir / "hello_glibc_startup"),
        ]
    )

    # PIE startup without relying on DT_RUNPATH.
    _run(
        common
        + [
            str(glibc_build / "csu" / "crti.o"),
            str(glibc_build / "csu" / "Scrt1.o"),
            str(src),
            str(glibc_build / "libc.so"),
            str(glibc_build / "csu" / "crtn.o"),
            "-o",
            str(out_dir / "hello_glibc_startup_norpath"),
        ]
    )

    print(f"ok: built glibc smoke artifacts in {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(os.sys.argv[1:]))
