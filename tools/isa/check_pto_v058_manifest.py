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
GIT_OID = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def load(root: Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def encoding_key(item: dict[str, Any], compiled: bool = False) -> tuple[tuple[int, int, int], ...]:
    parts = item.get("encoding", {}).get("parts", []) if compiled else item.get("encoding", [])
    return tuple((int(part["mask"], 0), int(part["match"], 0), int(part["width_bits"])) for part in parts)


def source_field_key(item: dict[str, Any]) -> tuple[Any, ...]:
    signedness = {"encoding-defined": None, "signed": True, "unsigned": False}
    return tuple(sorted(
        (
            field["name"],
            int(field["width"]),
            signedness[field["signedness"]],
            tuple(
                (
                    int(piece["instruction_lsb"]),
                    int(piece["value_lsb"]),
                    int(piece["width"]),
                )
                for piece in field["pieces"]
            ),
        )
        for field in item.get("fields", [])
    ))


def compiled_field_key(item: dict[str, Any]) -> tuple[Any, ...]:
    fields: dict[tuple[str, Any], list[tuple[int, int, int]]] = {}
    for part in item.get("encoding", {}).get("parts", []):
        part_base = int(part.get("index", 0)) * 32
        for field in part.get("fields", []):
            if str(field["name"]).startswith("PTOU"):
                continue
            pieces = tuple(
                (
                    part_base + int(piece["insn_lsb"]),
                    int(piece.get("value_lsb", 0)),
                    int(piece["width"]),
                )
                for piece in field.get("pieces", [])
            )
            fields.setdefault((field["name"], field.get("signed")), []).extend(pieces)
    result = []
    for (name, signed), pieces in fields.items():
        ordered = tuple(sorted(pieces, key=lambda piece: piece[1]))
        logical_width = max((piece[1] + piece[2] for piece in ordered), default=0)
        result.append((name, logical_width, signed, ordered))
    return tuple(sorted(result))


def source_constraint_key(item: dict[str, Any]) -> tuple[tuple[Any, ...], ...]:
    operators = {
        "equal": "==",
        "not-equal": "!=",
        "less-than": "<",
        "less-than-or-equal": "<=",
        "greater-than": ">",
        "greater-than-or-equal": ">=",
    }
    result = []
    for constraint in item.get("constraints", []):
        if constraint["operator"] == "one-of":
            result.append((constraint["field"], "one-of", tuple(int(value) for value in constraint["values"])))
        else:
            result.append((constraint["field"], operators[constraint["operator"]], int(constraint["value"])))
    return tuple(result)


def compiled_constraint_key(item: dict[str, Any]) -> tuple[tuple[str, str, int], ...]:
    return tuple(
        (constraint["field"], constraint["op"], int(constraint["value"], 0))
        for part in item.get("encoding", {}).get("parts", [])
        for constraint in part.get("constraints", [])
    )


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
    if not GIT_OID.fullmatch(str(lock.get("source", {}).get("commit", ""))):
        errors.append("PTO lock must pin an exact source commit")
    if not GIT_OID.fullmatch(str(lock.get("source", {}).get("tree", ""))):
        errors.append("PTO lock must pin an exact source tree")
    expected_catalogs = {
        "scalar_forms": 474,
        "command_forms": 99,
        "tile_operations": 109,
        "linx_vector_reservations": 6,
    }
    for name, count in expected_catalogs.items():
        entry = lock.get("catalogs", {}).get(name, {})
        if entry.get("count") != count or not SHA256.fullmatch(str(entry.get("sha256", ""))):
            errors.append(f"PTO lock must freeze {count} {name}")

    tiles = docs["tiles"].get("operations", [])
    if Counter(item.get("family") for item in tiles) != Counter({"TEPL": 87, "TLSU": 10, "CUBE": 12}):
        errors.append("tile inventory must be exactly 87 TEPL / 10 TLSU / 12 CUBE")
    source_forms = docs["scalars"].get("forms", []) + docs["commands"].get("forms", [])
    scalar_ids = {str(form["form_id"]) for form in docs["scalars"].get("forms", [])}
    if len(source_forms) != 573:
        errors.append("PTO scalar/block form inventory must contain exactly 573 forms")
    source_ids = [str(form["form_id"]) for form in source_forms]
    if len(source_ids) != len(set(source_ids)):
        errors.append("PTO scalar/block form identities must be unique")
    compiled_items = [
        item for item in docs["spec"].get("instructions", []) if item.get("pto_source_form_id")
    ]
    compiled = {
        str(item["pto_source_form_id"]): item
        for item in compiled_items
    }
    if len(compiled_items) != len(compiled):
        errors.append("compiled Linx profile must not duplicate PTO form identities")
    if len(compiled) != 573:
        errors.append("compiled Linx profile must attach exactly 573 PTO form identities")
    if set(compiled) != set(source_ids):
        errors.append("compiled Linx PTO form identity set must equal the canonical PTO set")
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
        if compiled_field_key(item) != source_field_key(form):
            errors.append(f"compiled PTO fields differ from source: {form_id}")
        if form_id in scalar_ids:
            if compiled_constraint_key(item) != source_constraint_key(form):
                errors.append(f"compiled PTO scalar constraints differ from source: {form_id}")
        elif item.get("pto_source_constraints") != form.get("constraints", []):
            errors.append(f"compiled PTO command constraints differ from source: {form_id}")

    source_variants = {
        (str(form["form_id"]), str(variant["name"])): (form, variant)
        for form in docs["commands"].get("forms", [])
        for variant in form.get("encoding_variants", [])
    }
    compiled_variants = {
        (str(item.get("pto_source_form_variant_of")), str(item["pto_source_form_variant"])): item
        for item in docs["spec"].get("instructions", [])
        if item.get("pto_source_form_variant")
    }
    if set(compiled_variants) != set(source_variants):
        errors.append("compiled PTO command variant set must equal the canonical PTO set")
    for key, (form, variant) in source_variants.items():
        item = compiled_variants.get(key)
        if item is None:
            continue
        expected_variant = {"encoding": variant["encoding"]}
        if (
            item.get("mnemonic"),
            item.get("asm"),
            item.get("length_bits"),
            encoding_key(item, True),
        ) != (
            form.get("mnemonic"),
            form.get("asm"),
            form.get("length_bits"),
            encoding_key(expected_variant),
        ):
            errors.append(f"compiled PTO command variant differs from source: {key}")
        if compiled_field_key(item) != source_field_key(form):
            errors.append(f"compiled PTO command variant fields differ from source: {key}")
        if item.get("pto_source_constraints") != form.get("constraints", []):
            errors.append(f"compiled PTO command variant constraints differ from source: {key}")

    linx_only = [
        item
        for item in docs["spec"].get("instructions", [])
        if not item.get("pto_source_form_id") and not item.get("pto_source_form_variant")
    ]
    vector_headers = {"BSTART.VPAR", "BSTART.VSEQ", "C.BSTART.VPAR", "C.BSTART.VSEQ"}
    non_vector_delta = sorted(
        str(item.get("mnemonic"))
        for item in linx_only
        if not str(item.get("mnemonic")).startswith("V.")
        and str(item.get("mnemonic")) not in vector_headers
    )
    if len(linx_only) != 188 or sum(str(item.get("mnemonic")).startswith("V.") for item in linx_only) != 184:
        errors.append("Linx-only delta must contain exactly 184 V.* forms plus four vector block headers")
    if non_vector_delta:
        errors.append(f"non-vector Linx-only scalar/block forms leaked: {non_vector_delta}")

    required_command_mnemonics = {
        "BSTART.MGATHER.MASK",
        "BSTART.MSCATTER.MASK",
        "BSTART.MGATHER.CAS",
    }
    command_mnemonics = {form.get("mnemonic") for form in docs["commands"].get("forms", [])}
    if not required_command_mnemonics <= command_mnemonics:
        errors.append("PTO block catalog must retain MGATHER.MASK, MSCATTER.MASK, and MGATHER.CAS")
    required_tile_names = {"MGATHER_MASK", "MSCATTER_MASK", "MGATHER_CAS"}
    if not required_tile_names <= {item.get("name") for item in tiles}:
        errors.append("PTO tile catalog must retain MGATHER_MASK, MSCATTER_MASK, and MGATHER_CAS")

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
