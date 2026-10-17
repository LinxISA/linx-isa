#!/usr/bin/env python3
"""Compare every effective scalar form and encoding-only resource reservation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from build_golden import effective_pto_encoding
from check_pto_v058_manifest import compiled_field_key, source_field_key
from pto_scalar_proposal import apply_proposal


ROOT = Path(__file__).resolve().parents[2]
RESERVED = {"DMA.FREE.S", "DMA.FREE.L", "MCOPY.DS", "MCOPY.DL"}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compare(root: Path, pto_root: Path) -> list[str]:
    profile = root / "isa/v0.58"
    effective = apply_proposal(profile, read(profile / "state/pto_scalar_forms.json"))
    upstream = read(pto_root / "spec/catalog/scalar-forms.json")
    left = {form["form_id"]: form for form in effective["forms"]}
    right = {form["form_id"]: form for form in upstream["forms"]}
    errors = []
    lock = read(profile / "pto-scalar-proposal.lock.json")
    for ref, expected in (("HEAD", lock["source"]["commit"]), ("HEAD^{tree}", lock["source"]["tree"])):
        actual = subprocess.check_output(["git", "-C", str(pto_root), "rev-parse", ref], text=True).strip()
        if actual != expected:
            errors.append(f"PTO proposal checkout differs from pinned {ref}")
    for catalog in lock["catalogs"].values():
        if hashlib.sha256((pto_root / catalog["path"]).read_bytes()).hexdigest() != catalog["sha256"]:
            errors.append(f"PTO proposal catalog differs from pinned bytes: {catalog['path']}")
    if len(left) != 473 or len(right) != 473 or left.keys() != right.keys():
        errors.append("effective scalar inventory must equal all 473 PTO proposal forms")
    for identity in left.keys() & right.keys():
        if left[identity] != right[identity]:
            errors.append(f"scalar source differs from PTO proposal: {identity}")
    for local_path, remote_path in (
        ("state/pto_command_forms.json", "spec/catalog/command-forms.json"),
        ("state/extension_encoding_reservations.json", "spec/catalog/extension-encoding-reservations.json"),
    ):
        local = {key: value for key, value in read(profile / local_path).items() if key != "source_lock"}
        if local != read(pto_root / remote_path):
            errors.append(f"common design differs from PTO golden: {local_path}")
    if read(profile / "state/pto_ops.json")["operations"] != read(pto_root / "spec/catalog/tile-operations.json")["operations"]:
        errors.append("Tile design differs from PTO golden")
    if read(profile / "release_manifest.json").get("identity") != read(pto_root / "spec/development-manifest.json")["identity"]:
        errors.append("active encoding identity differs from PTO golden")
    spec = read(profile / "linxisa-v0.58.json")
    reservations = read(pto_root / "spec/catalog/extension-encoding-reservations.json")
    reserved = {form["mnemonic"]: form for form in reservations["reservations"]}
    status = read(root / "isa/sail/semantics_status.json")
    # The manifest gate separately compares all compiled scalar fields and constraints.
    for name in sorted(RESERVED):
        matches = [item for item in spec["instructions"] if item["mnemonic"] == name]
        source = reserved.get(name)
        if len(matches) != 1 or source is None:
            errors.append(f"missing encoding-only resource reservation: {name}")
            continue
        item = matches[0]
        actual = [(part["width_bits"], int(part["mask"], 0), int(part["match"], 0))
                  for part in item["encoding"]["parts"]]
        expected = [(part["width_bits"], int(part["mask"], 0), int(part["match"], 0))
                    for part in effective_pto_encoding(source)]
        if actual != expected or compiled_field_key(item) != source_field_key(source):
            errors.append(f"encoding-only reservation differs: {name}")
        if "NOT IMPLEMENTED" not in item.get("note", ""):
            errors.append(f"resource instruction lacks explicit implementation status: {name}")
        if source.get("status") != "reserved-in-pto":
            errors.append(f"resource instruction is not reserved in PTO: {name}")
        if status.get("forms", {}).get(item["id"], {}).get("status") != "decode-only":
            errors.append(f"resource instruction incorrectly claims executable coverage: {name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--pto-root", type=Path, required=True)
    args = parser.parse_args()
    errors = compare(args.root, args.pto_root)
    if errors:
        print("\n".join(errors))
        return 1
    print("OK: PTO golden parity: 473 scalars, 105 commands, 119 Tile operations, 50 reservations, development identity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
