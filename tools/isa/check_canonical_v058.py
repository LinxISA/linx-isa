#!/usr/bin/env python3
"""Enforce the standalone LinxISA 0.58 release surface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    spec_path = root / "isa/v0.58/linxisa-v0.58.json"
    if not spec_path.is_file():
        return [f"missing LinxISA 0.58 compiled spec: {spec_path}"]
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("version") != "0.58.0":
        errors.append(f"compiled profile version must be 0.58.0, got {spec.get('version')!r}")
    mnemonics = {str(item.get("mnemonic")) for item in spec.get("instructions", [])}
    required = {
        "C.B.IOS", "BSTART.GMOV", "BSTART.VPAR", "BSTART.VSEQ",
        "C.BSTART.VPAR", "C.BSTART.VSEQ", "V.QPOP", "V.QPUSH",
        "BSTART.MGATHER.CAS", "BSTART.MGATHER.MASK", "BSTART.MSCATTER.MASK",
    }
    for mnemonic in sorted(required - mnemonics):
        errors.append(f"required LinxISA 0.58 mnemonic missing: {mnemonic}")
    retired = {
        "B.IOD", "BSTART.PAR", "BSTART.TMA", "BSTART.ACCCVT",
        "C.B.DIM",
    }
    for mnemonic in sorted(retired & mnemonics):
        errors.append(f"retired 0.57 mnemonic still decodes: {mnemonic}")
    sys.path.insert(0, str(root / "tools/isa"))
    import check_pto_v058_manifest  # type: ignore

    errors.extend(check_pto_v058_manifest.validate(root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
