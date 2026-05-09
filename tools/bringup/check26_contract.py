#!/usr/bin/env python3
"""Compatibility gate for the historical check26 contract command.

The original check26 YAML gate was retired with the v0.56 canonical migration,
but repo playbooks and skills still invoke this command as a mandatory ISA
contract closeout step. Keep the command stable and route it to the live v0.56
machine-readable contract checks.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(root: Path, args: list[str]) -> None:
    proc = subprocess.run(args, cwd=str(root), text=True)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate the live LinxISA v0.56 contract")
    ap.add_argument("--root", default=".", help="Repository root")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    py = sys.executable
    _run(root, [py, "tools/isa/build_golden.py", "--profile", "v0.56", "--check"])
    _run(root, [py, "tools/isa/validate_spec.py", "--profile", "v0.56"])
    _run(root, [py, "tools/isa/check_canonical_v056.py", "--root", str(root)])
    print("ok: check26 compatibility gate passed for canonical v0.56")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
