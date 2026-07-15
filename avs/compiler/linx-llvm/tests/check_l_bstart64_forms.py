#!/usr/bin/env python3
"""Check the canonical v0.56.5 64-bit L.BSTART form matrix."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


_ADDRESS_RE = re.compile(r"^\s*[0-9a-fA-F]+:\s+")
_BYTE_RE = re.compile(r"^[0-9a-fA-F]{2}$")
_EXPECTED = [
    ("L.BSTART.STD", "FALL"),
    ("L.BSTART.STD", "DIRECT"),
    ("L.BSTART.STD", "COND"),
    ("L.BSTART.STD", "CALL"),
    ("L.BSTART.FP", "FALL"),
    ("L.BSTART.FP", "DIRECT"),
    ("L.BSTART.FP", "COND"),
    ("L.BSTART.FP", "CALL"),
    ("L.BSTART.SYS", "FALL"),
]


def extract_forms(path: Path) -> list[tuple[str, str]]:
    forms: list[tuple[str, str]] = []
    for line in path.read_text(errors="replace").splitlines():
        if not _ADDRESS_RE.match(line):
            continue
        _, rest = line.split(":", 1)
        tokens = rest.strip().split()
        while tokens and _BYTE_RE.fullmatch(tokens[0]):
            tokens.pop(0)
        if len(tokens) < 2 or not tokens[0].upper().startswith("L.BSTART."):
            continue
        forms.append((tokens[0].upper(), tokens[1].rstrip(",").upper()))
    return forms


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--objdump", type=Path, required=True)
    parser.add_argument("--label", default="")
    args = parser.parse_args(argv)

    if not args.objdump.is_file():
        print(f"error: objdump file not found: {args.objdump}", file=sys.stderr)
        return 1

    actual = extract_forms(args.objdump)
    if actual != _EXPECTED:
        label = f"{args.label}: " if args.label else ""
        print(f"error: {label}unexpected L.BSTART form matrix", file=sys.stderr)
        print(f"  expected: {_EXPECTED}", file=sys.stderr)
        print(f"  actual:   {actual}", file=sys.stderr)
        return 2

    label = f"{args.label}: " if args.label else ""
    print(f"ok: {label}{len(_EXPECTED)} canonical L.BSTART forms present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
