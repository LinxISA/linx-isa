#!/usr/bin/env python3
"""Check exact PTO 0.58 scalar/block alignment and Linx vector reservations."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROFILE = Path("isa/v0.58")
HASH = re.compile(r"^[0-9a-f]{64}$")


def load(root: Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def encoding_key(item: dict[str, Any], compiled: bool = False) -> tuple[tuple[int, int, int], ...]:
    parts = item.get("encoding", {}).get("parts", []) if compiled else item.get("encoding", [])
    return tuple((int(part["mask"], 0), int(part["match"], 0), int(part["width_bits"])) for part in parts)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    paths = {
        "lock": "isa/v0.58/pto-spec.lock.json",
        "tiles": "isa/v0.58/state/pto_ops.json",
        "commands": "isa/v0.58/state/pto_command_forms.json",
        "scalars": "isa/v0.58/state/pto_scalar_forms.json",
        "reservations": "isa/v0.58/state/linx_vector_reservations.json",
        "shared": "isa/v0.58/state/shared_tile_registers.json",
        "release": "isa/v0.58/release_manifest.json",
        "spec": "isa/v0.58/linxisa-v0.58.json",
    }
    missing = [relative for relative in paths.values() if not (root / relative).is_file()]
    if missing:
        return [f"missing PTO/Linx 0.58 artifact: {relative}" for relative in missing]
    docs = {name: load(root, relative) for name, relative in paths.items()}
    lock = docs["lock"]
    if lock.get("release") != "0.58.0" or lock.get("encoding_abi") != "pto-isa-0.58.0-mode-function-v1":
        errors.append("PTO lock has the wrong 0.58 release/ABI identity")
    if not HASH.fullmatch(str(lock.get("source", {}).get("commit", ""))):
        errors.append("PTO lock must pin an exact source commit")
    if not HASH.fullmatch(str(lock.get("source", {}).get("tree", ""))):
        errors.append("PTO lock must pin an exact source tree")
    expected_catalogs = {
        "scalar_forms": 474,
        "command_forms": 96,
        "tile_operations": 106,
        "linx_vector_reservations": 6,
    }
    for name, count in expected_catalogs.items():
        entry = lock.get("catalogs", {}).get(name, {})
        if entry.get("count") != count or not HASH.fullmatch(str(entry.get("sha256", ""))):
            errors.append(f"PTO lock must freeze {count} {name}")

    tiles = docs["tiles"].get("operations", [])
    if Counter(item.get("family") for item in tiles) != Counter({"TEPL": 87, "TMA": 7, "CUBE": 12}):
        errors.append("tile inventory must be exactly 87 TEPL / 7 TMA / 12 CUBE")
    source_forms = docs["scalars"].get("forms", []) + docs["commands"].get("forms", [])
    if len(source_forms) != 570:
        errors.append("PTO scalar/block form inventory must contain exactly 570 forms")
    compiled = {
        str(item["pto_source_form_id"]): item
        for item in docs["spec"].get("instructions", []) if item.get("pto_source_form_id")
    }
    if len(compiled) != 570:
        errors.append("compiled Linx profile must attach exactly 570 PTO form identities")
    for form in source_forms:
        form_id = str(form["form_id"])
        item = compiled.get(form_id)
        if item is None:
            errors.append(f"missing compiled PTO form {form_id}")
            continue
        if (item.get("mnemonic"), item.get("asm"), item.get("length_bits"), encoding_key(item, True)) != (
            form.get("mnemonic"), form.get("asm"), form.get("length_bits"), encoding_key(form)
        ):
            errors.append(f"compiled PTO form differs from source: {form_id}")

    compiled_by_mnemonic = {item["mnemonic"]: item for item in docs["spec"].get("instructions", [])}
    reservations = docs["reservations"].get("reservations", [])
    if len(reservations) != 6:
        errors.append("PTO must reserve exactly six Linx vector encodings")
    for reservation in reservations:
        item = compiled_by_mnemonic.get(reservation["mnemonic"])
        if item is None or encoding_key(item, True) != encoding_key(reservation):
            errors.append(f"Linx vector reservation mismatch: {reservation['mnemonic']}")

    shared = docs["shared"]
    if shared.get("register_count") != 256 or shared.get("register_names", {}).get("syntax") != "S<absolute-index>":
        errors.append("Shared tile bank must expose absolute S0..S255 names")
    if shared.get("scope") != {"private_to": "core", "shared_by": "four PEs in that core"}:
        errors.append("Shared tile bank must be core-private and shared by four PEs")
    mask = shared.get("pe_mask", {})
    if mask.get("width") != 4 or mask.get("zero_behavior") != "nop" or mask.get("absent_value") != "0b1111":
        errors.append("Shared tile PE mask must be optional 4-bit predicate with zero=Nop")
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
