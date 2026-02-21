#!/usr/bin/env python3
"""Patch hard-coded user-specific paths in docs/runbooks.

This is intentionally conservative: it only rewrites a small set of known
hard-coded prefixes to repo-relative or variable-based forms.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# (old, new)
REPLACEMENTS: list[tuple[str, str]] = [
    ("/Users/zhoubot/linx-isa/", ""),
    ("/Users/zhoubot/linx-isa", "."),
    ("cd /Users/zhoubot/linx-isa", "cd ."),
    ("/Users/zhoubot/linux/", "${LINUX_ROOT}/"),
    ("/Users/zhoubot/linux", "${LINUX_ROOT}"),
    ("/Users/zhoubot/llvm-project/", "${LLVM_ROOT}/"),
    ("/Users/zhoubot/llvm-project", "${LLVM_ROOT}"),
    ("/Users/zhoubot/qemu/", "${QEMU_ROOT}/"),
    ("/Users/zhoubot/qemu", "${QEMU_ROOT}"),
    ("/Users/zhoubot/pyCircuit", "${PYCIRCUIT_ROOT}"),
    ("/Users/zhoubot/LinxCore", "${LINXCORE_ROOT}"),
]

TARGETS = [
    REPO_ROOT / "docs" / "bringup",
    REPO_ROOT / "docs" / "reference",
    REPO_ROOT / "avs" / "qemu" / "README.md",
]


def patch_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() not in {".md", ".py", ".sh", ".yaml", ".yml"}:
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    orig = text
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed: list[Path] = []
    for t in TARGETS:
        if t.is_file():
            if patch_file(t):
                changed.append(t)
            continue
        if t.is_dir():
            for p in t.rglob("*"):
                if patch_file(p):
                    changed.append(p)

    if changed:
        print("patched files:")
        for p in changed:
            print("-", p.relative_to(REPO_ROOT))
    else:
        print("no changes")


if __name__ == "__main__":
    main()
