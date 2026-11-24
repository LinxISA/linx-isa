#!/usr/bin/env python3
"""Check the released PTO encoding delta against the active Linx catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_golden import effective_pto_encoding
from check_pto_v058_manifest import (
    compiled_constraint_key,
    compiled_field_key,
    source_constraint_key,
    source_field_key,
)


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_CONSTRAINT_ADDITIONS = {
    ("B.DATR", "CMode"): {6, 7},
    ("BSTART.TMOV", "DataType"): {15, 21},
}


def read(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def encoding_parts(parts: list[dict]) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (int(part["width_bits"]), int(part["mask"], 0), int(part["match"], 0))
        for part in parts
    )


def pattern64(parts: list[dict]) -> tuple[int, int]:
    mask = match = offset = 0
    for width, part_mask, part_match in encoding_parts(parts):
        if width <= 0 or not 0 <= part_match < 1 << width or part_match & ~part_mask:
            raise ValueError("invalid fixed bits in a 64-bit encoding")
        if not 0 <= part_mask < 1 << width:
            raise ValueError("invalid mask in a 64-bit encoding")
        mask |= part_mask << offset
        match |= part_match << offset
        offset += width
    if offset != 64:
        raise ValueError(f"expected 64 encoded bits, got {offset}")
    return mask, match


def compare(root: Path) -> tuple[dict[str, int], list[str]]:
    baseline = read(root, "isa/v0.58/linxisa-v0.58.json")
    scalar = read(root, "isa/v0.59/state/pto_scalar_forms.json")
    command = read(root, "isa/v0.59/state/pto_command_forms.json")
    forms = scalar["forms"] + command["forms"]
    scoped = scalar["scoped_forms"]
    bound = [
        item for item in baseline["instructions"] if item.get("pto_source_form_id")
    ]
    current = {item["pto_source_form_id"]: item for item in bound}
    upstream = {form["form_id"]: form for form in forms}
    errors = []
    if len(current) != len(bound) or len(upstream) != len(forms) or current.keys() != upstream.keys():
        errors.append("unqualified PTO source identities differ from the active Linx bindings")

    constraint_additions: dict[tuple[str, str], set[int]] = {}
    for identity in sorted(current.keys() & upstream.keys()):
        item, form = current[identity], upstream[identity]
        actual = encoding_parts(item["encoding"]["parts"])
        expected = encoding_parts(effective_pto_encoding(form))
        if actual != expected or item["mnemonic"] != form["mnemonic"] or item["asm"] != form["asm"]:
            errors.append(f"unqualified encoding or spelling changed for {identity}")
            continue
        if compiled_field_key(item) != source_field_key(form):
            errors.append(f"unqualified operand fields changed for {identity}")
            continue
        prior = dict(compiled_constraint_key(item, form))
        updated = dict(source_constraint_key(form))
        widths = {field["name"]: int(field["width"]) for field in form["fields"]}
        for field in prior.keys() | updated.keys():
            # The compiled catalog omits a predicate when the source accepts
            # every value in the encoded field's domain.
            unrestricted = tuple(range(1 << widths[field]))
            old_values = prior.get(field, unrestricted)
            new_values = updated.get(field, unrestricted)
            if old_values == new_values:
                continue
            if not set(old_values) <= set(new_values):
                errors.append(f"a previously accepted {field} value was removed from {identity}")
            key = (form["mnemonic"], field)
            constraint_additions.setdefault(key, set()).update(set(new_values) - set(old_values))
    if constraint_additions != EXPECTED_CONSTRAINT_ADDITIONS:
        errors.append(f"unreviewed unqualified constraint delta {constraint_additions}")

    old_reservations = read(root, "isa/v0.58/state/extension_encoding_reservations.json")
    new_reservations = read(root, "isa/v0.59/state/extension_encoding_reservations.json")
    if old_reservations["reservations"] != new_reservations["reservations"]:
        errors.append("the released PTO extension reservation rows differ from Linx v0.58")

    linx_patterns = [
        (item["id"], *pattern64(item["encoding"]["parts"]))
        for item in baseline["instructions"] if item["length_bits"] == 64
    ]
    for form in scoped:
        if form["base_form_id"] not in upstream:
            errors.append(f"scoped form {form['form_id']} has no unqualified source")
        mask, match = pattern64(form["encoding"])
        for linx_id, linx_mask, linx_match in linx_patterns:
            if (match ^ linx_match) & mask & linx_mask == 0:
                errors.append(f"scoped encoding {form['form_id']} overlaps Linx {linx_id}")
    return {"common": len(upstream), "scoped": len(scoped), "linx_64_bit": len(linx_patterns)}, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        counts, errors = compare(args.root)
    except (KeyError, OSError, ValueError) as error:
        raise SystemExit(f"PTO v0.59.1 alignment failed: {error}") from error
    if errors:
        raise SystemExit("\n".join(errors))
    print(
        f"PTO v0.59.1 encoding alignment passed for {counts['common']} common forms "
        f"and {counts['scoped']} scoped forms against {counts['linx_64_bit']} 64-bit forms in the v0.58 comparison baseline"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
