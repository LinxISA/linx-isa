#!/usr/bin/env python3
"""Require specific mnemonic spellings in an llvm-objdump artifact."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analyze_coverage import canonicalize_mnemonic, extract_mnemonics_from_objdump


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Check that an objdump contains required mnemonic tokens"
    )
    parser.add_argument("--objdump", type=Path, required=True, help="llvm-objdump -d output")
    parser.add_argument("--label", default="", help="test label for diagnostics")
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        help="required mnemonic; may be passed more than once",
    )
    args = parser.parse_args(argv)

    if not args.objdump.is_file():
        print(f"error: objdump file not found: {args.objdump}", file=sys.stderr)
        return 1
    if not args.require:
        print("error: at least one --require mnemonic is required", file=sys.stderr)
        return 1

    seen = extract_mnemonics_from_objdump(args.objdump)
    required = {canonicalize_mnemonic(m) for m in args.require}
    missing = sorted(required - seen)
    if missing:
        label = f"{args.label}: " if args.label else ""
        print(
            f"error: {label}missing required mnemonics in {args.objdump}: "
            + ", ".join(missing),
            file=sys.stderr,
        )
        return 2

    label = f"{args.label}: " if args.label else ""
    print(f"ok: {label}{len(required)} required mnemonics present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
