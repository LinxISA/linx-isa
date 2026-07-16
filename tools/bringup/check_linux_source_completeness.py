#!/usr/bin/env python3
"""Reject a Linx Linux checkout whose required assembly sources are not tracked."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATCH_SHA256 = "3c677141f95bb4b2369efd44b791163edde5558c851458ee6376a1c700df7a9f"
REQUIRED_SOURCES = (
    "arch/linx/boot/loader.S",
    "arch/linx/boot/loader.lds.S",
    "arch/linx/kernel/efi-header.S",
    "arch/linx/kernel/entry.S",
    "arch/linx/kernel/head.S",
    "arch/linx/kernel/qemu_debug.S",
    "arch/linx/kernel/vdso/flush_icache.S",
    "arch/linx/kernel/vdso/getcpu.S",
    "arch/linx/kernel/vdso/note.S",
    "arch/linx/kernel/vdso/rt_sigreturn.S",
    "arch/linx/kernel/vdso/vdso.S",
    "arch/linx/kernel/vdso/vdso.lds.S",
    "arch/linx/kernel/vmlinux.lds.S",
    "arch/linx/lib/memset.S",
    "arch/linx/lib/uaccess.S",
)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--linux-root", type=Path, default=ROOT / "kernel" / "linux")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    linux_root = args.linux_root.resolve()
    if not (linux_root / ".git").exists():
        print(f"E_LINUX_SOURCE_NOT_GIT: {linux_root}", file=sys.stderr)
        return 2

    listed = git(linux_root, "ls-files", "--", "arch/linx")
    if listed.returncode != 0:
        print(listed.stderr.rstrip(), file=sys.stderr)
        return 2
    tracked = set(listed.stdout.splitlines())
    errors: list[str] = []
    discovered_sources = sorted((linux_root / "arch" / "linx").rglob("*.S"))

    for relative in REQUIRED_SOURCES:
        if not (linux_root / relative).is_file():
            errors.append(f"E_LINUX_SOURCE_MISSING: {relative}")
        elif relative not in tracked:
            errors.append(f"E_LINUX_SOURCE_UNTRACKED: {relative}")

    for source in discovered_sources:
        relative = source.relative_to(linux_root).as_posix()
        if relative not in tracked:
            errors.append(f"E_LINUX_SOURCE_UNTRACKED: {relative}")
        ignored = git(linux_root, "check-ignore", "--no-index", "--quiet", "--", relative)
        if ignored.returncode == 0:
            errors.append(f"E_LINUX_SOURCE_IGNORED: {relative}")
        elif ignored.returncode != 1:
            errors.append(f"E_LINUX_SOURCE_IGNORE_CHECK: {relative}")
        source_text = source.read_text(encoding="utf-8", errors="replace")
        if re.search(r"\bb\.attr\b", source_text):
            errors.append(f"E_LINUX_SOURCE_RETIRED_B_ATTR: {relative}")
        if "L.BSTART" in source_text:
            errors.append(f"E_LINUX_SOURCE_RETIRED_L_BSTART: {relative}")

    if errors:
        print("\n".join(dict.fromkeys(errors)), file=sys.stderr)
        return 1

    head = git(linux_root, "rev-parse", "HEAD").stdout.strip()
    print(
        "ok: Linx Linux assembly sources are complete "
        f"({len(REQUIRED_SOURCES)} tracked, linux_head={head}, "
        f"baseline_patch_sha256={BASELINE_PATCH_SHA256})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
