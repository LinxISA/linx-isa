#!/usr/bin/env python3
"""
Fail if any tracked text file contains CJK characters.

This is intended to keep the public repo English-only.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def _git_ls_files(repo_root: Path) -> List[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=str(repo_root), text=True)
    return [l.strip() for l in out.splitlines() if l.strip()]


def _is_probably_binary(data: bytes) -> bool:
    return b"\0" in data[:4096]


def _has_cjk_char(ch: str) -> bool:
    o = ord(ch)
    # CJK Unified Ideographs + Extension A + Compatibility Ideographs + CJK punctuation
    return (0x3400 <= o <= 0x4DBF) or (0x4E00 <= o <= 0x9FFF) or (0xF900 <= o <= 0xFAFF) or (0x3000 <= o <= 0x303F)


def _first_cjk(text: str) -> Tuple[int, int, str]:
    line = 1
    col = 1
    for ch in text:
        if ch == "\n":
            line += 1
            col = 1
            continue
        if _has_cjk_char(ch):
            return line, col, ch
        col += 1
    return 1, 1, ""


def _skip_extension(path: str) -> bool:
    ext = Path(path).suffix.lower()
    return ext in {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".zip",
        ".gz",
        ".xz",
        ".bz2",
        ".7z",
        ".jar",
        ".class",
        ".o",
        ".a",
        ".so",
        ".dylib",
        ".bin",
        ".elf",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", help="Repo root (for git ls-files)")
    ap.add_argument("--allow-prefix", action="append", default=[], help="Allow path prefix (repeatable)")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    allow_paths = [p.rstrip("/") for p in args.allow_prefix]

    failures: List[str] = []
    for rel in _git_ls_files(repo_root):
        if _skip_extension(rel):
            continue
        if any(rel == p or rel.startswith(p + "/") or rel.startswith(p + ".") for p in allow_paths):
            continue
        p = repo_root / rel
        try:
            data = p.read_bytes()
        except Exception:
            continue
        if _is_probably_binary(data):
            continue
        text = data.decode("utf-8", errors="ignore")
        if not text:
            continue
        if any(_has_cjk_char(ch) for ch in text):
            line, col, ch = _first_cjk(text)
            failures.append(f"{rel}:{line}:{col}: contains CJK char {ch!r}")

    if failures:
        for f in failures[:200]:
            print(f, file=sys.stderr)
        if len(failures) > 200:
            print(f"... {len(failures) - 200} more", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
