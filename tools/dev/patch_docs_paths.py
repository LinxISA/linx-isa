#!/usr/bin/env python3
"""Patch hard-coded *user-specific* absolute paths in docs/runbooks.

Goal: make checked-in docs and gate reports portable across machines/OSes.

This script is intentionally conservative:
- it targets doc-like file extensions (including .json gate artifacts)
- it rewrites common absolute root prefixes to either repo-root variables
  or external-lane variables

It does **not** attempt to validate the resulting paths; it only de-hardcodes.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Regex replacements (pattern -> replacement)
# Order matters: rewrite the in-repo prefix first.
REPLACEMENTS_RX: list[tuple[re.Pattern[str], str]] = [
    # In-repo absolute paths.
    # Match as a path token even when followed by whitespace/quotes/commas, etc.
    (re.compile(r"/(Users|home)/[^/]+/linx-isa(?=(/|\s|\"|'|`|,|:|\)|\]|\}|$))"), "${LINXISA_ROOT}"),

    # External-lane roots (typical standalone clones outside the superproject).
    (re.compile(r"/(Users|home)/[^/]+/linux(?=(/|\s|\"|'|`|,|:|\)|\]|\}|$))"), "${LINUX_ROOT}"),
    (re.compile(r"/(Users|home)/[^/]+/glibc(?=(/|\s|\"|'|`|,|:|\)|\]|\}|$))"), "${GLIBC_ROOT}"),
    (re.compile(r"/(Users|home)/[^/]+/musl(?=(/|\s|\"|'|`|,|:|\)|\]|\}|$))"), "${MUSL_ROOT}"),
    (re.compile(r"/(Users|home)/[^/]+/llvm-project(?=(/|\s|\"|'|`|,|:|\)|\]|\}|$))"), "${LLVM_ROOT}"),
    (re.compile(r"/(Users|home)/[^/]+/qemu(?=(/|\s|\"|'|`|,|:|\)|\]|\}|$))"), "${QEMU_ROOT}"),
    (re.compile(r"/(Users|home)/[^/]+/pyCircuit(?=(/|\s|\"|'|`|,|:|\)|\]|\}|$))"), "${PYCIRCUIT_ROOT}"),
    (re.compile(r"/(Users|home)/[^/]+/LinxCore(?=(/|\s|\"|'|`|,|:|\)|\]|\}|$))"), "${LINXCORE_ROOT}"),

    # Normalize common command snippets.
    (re.compile(r"\bcd\s+\$\{LINXISA_ROOT\}\b"), "cd ${LINXISA_ROOT}"),
]

TARGETS = [
    REPO_ROOT / "docs" / "bringup",
    REPO_ROOT / "docs" / "reference",
    REPO_ROOT / "avs" / "qemu" / "README.md",
    # Some bring-up artifacts are tracked under out/ for now.
    REPO_ROOT / "out" / "bringup",
]


def patch_file(path: Path) -> bool:
    if not path.is_file():
        return False

    # Only patch doc-like files (keep this conservative).
    if path.suffix.lower() not in {".md", ".adoc", ".py", ".sh", ".yaml", ".yml", ".json"}:
        return False

    text = path.read_text(encoding="utf-8", errors="replace")
    orig = text

    for rx, repl in REPLACEMENTS_RX:
        text = rx.sub(repl, text)

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
