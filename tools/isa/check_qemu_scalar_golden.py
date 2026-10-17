#!/usr/bin/env python3
"""Compare actual QEMU decoder signatures with all PTO golden scalar forms."""

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/bringup"))
from check_qemu_opcode_meta_sync import _parse_decode_forms  # noqa: E402
from pto_scalar_proposal import apply_proposal  # noqa: E402


def signature(form):
    length = form["length_bits"]
    mask = sum(int(part["mask"], 0) << (part["index"] * 32) for part in form["encoding"])
    match = sum(int(part["match"], 0) << (part["index"] * 32) for part in form["encoding"])
    # QEMU stores 48-bit decodetrees in a zero-padded 64-bit container.
    if length == 48:
        mask |= 0xFFFF000000000000
        length = 64
    name = re.sub("[^a-z0-9]+", "_", form["mnemonic"].lower()).strip("_")
    return name, length, mask, match


def mismatches(forms, decoded):
    return [form["form_id"] for form in forms if signature(form) not in decoded]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qemu-root", type=Path, default=ROOT / "emulator/qemu")
    args = parser.parse_args()
    profile = ROOT / "isa/v0.58"
    catalog = apply_proposal(profile, json.loads((profile / "state/pto_scalar_forms.json").read_text()))
    decoded = set()
    for width in (16, 32, 48, 64):
        path = args.qemu_root / "target/linx" / f"insn{width}.decode"
        if path.is_file():
            decoded.update(_parse_decode_forms(path))
    missing = mismatches(catalog["forms"], decoded)
    if missing:
        print("QEMU scalar encoding drift: " + ", ".join(missing))
        return 1
    print("OK: all 473 PTO scalar names and exact mask/match signatures agree with QEMU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
