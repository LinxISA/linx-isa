#!/usr/bin/env python3
"""Check exact PTO 0.58.3 common-subset alignment and Linx extensions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from build_golden import effective_pto_encoding, singleton_pto_fields


ROOT = Path(__file__).resolve().parents[2]
PROFILE = Path("isa/v0.58")
GIT_OID = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
EXTENSION_RESERVATION_COUNT = 40


def load(root: Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def encoding_key(item: dict[str, Any], compiled: bool = False) -> tuple[tuple[int, int, int], ...]:
    parts = item.get("encoding", {}).get("parts", []) if compiled else item.get("encoding", [])
    return tuple((int(part["mask"], 0), int(part["match"], 0), int(part["width_bits"])) for part in parts)


def source_encoding_key(
    item: dict[str, Any], encoding: list[dict[str, Any]] | None = None
) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (int(part["mask"], 0), int(part["match"], 0), int(part["width_bits"]))
        for part in effective_pto_encoding(item, encoding)
    )


def reservation_covers(reservation: dict[str, Any], item: dict[str, Any]) -> bool:
    reserved = encoding_key(reservation)
    concrete = encoding_key(item, True)
    if len(reserved) != len(concrete):
        return False
    return all(
        reserved_width == concrete_width
        and concrete_mask & reserved_mask == reserved_mask
        and concrete_match & reserved_mask == reserved_match
        for (reserved_mask, reserved_match, reserved_width), (
            concrete_mask,
            concrete_match,
            concrete_width,
        ) in zip(reserved, concrete)
    )


def source_field_key(
    item: dict[str, Any], encoding: list[dict[str, Any]] | None = None
) -> tuple[Any, ...]:
    signedness = {"encoding-defined": None, "signed": True, "unsigned": False}
    encoding_masks = [
        int(part["mask"], 0) for part in effective_pto_encoding(item, encoding)
    ]

    def is_variable(field: dict[str, Any]) -> bool:
        for piece in field["pieces"]:
            instruction_lsb = int(piece["instruction_lsb"])
            part_index, local_lsb = divmod(instruction_lsb, 32)
            piece_mask = ((1 << int(piece["width"])) - 1) << local_lsb
            if part_index >= len(encoding_masks) or encoding_masks[part_index] & piece_mask != piece_mask:
                return True
        return False

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
        if is_variable(field)
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


def _constraint_domains(
    constraints: list[dict[str, Any]],
    widths: dict[str, int],
    *,
    compiled: bool,
) -> tuple[tuple[str, tuple[int, ...]], ...]:
    domains = {field: set(range(1 << width)) for field, width in widths.items()}
    for constraint in constraints:
        field = str(constraint["field"])
        if field not in domains:
            continue
        operator = str(constraint["op"] if compiled else constraint["operator"])
        if operator == "one-of":
            values = {int(value) for value in constraint["values"]}
            domains[field] &= values
            continue
        value = int(constraint["value"], 0) if compiled else int(constraint["value"])
        predicates = {
            "equal": lambda candidate: candidate == value,
            "==": lambda candidate: candidate == value,
            "not-equal": lambda candidate: candidate != value,
            "!=": lambda candidate: candidate != value,
            "less-than": lambda candidate: candidate < value,
            "<": lambda candidate: candidate < value,
            "less-than-or-equal": lambda candidate: candidate <= value,
            "<=": lambda candidate: candidate <= value,
            "greater-than": lambda candidate: candidate > value,
            ">": lambda candidate: candidate > value,
            "greater-than-or-equal": lambda candidate: candidate >= value,
            ">=": lambda candidate: candidate >= value,
        }
        domains[field] = {candidate for candidate in domains[field] if predicates[operator](candidate)}
    return tuple(sorted((field, tuple(sorted(values))) for field, values in domains.items()))


def source_constraint_key(item: dict[str, Any]) -> tuple[tuple[str, tuple[int, ...]], ...]:
    widths = {str(field["name"]): int(field["width"]) for field in item.get("fields", [])}
    variable_fields = {str(field[0]) for field in source_field_key(item)}
    constrained = {
        str(constraint["field"])
        for constraint in item.get("constraints", [])
        if str(constraint["field"]) in variable_fields
    }
    return _constraint_domains(
        item.get("constraints", []),
        {field: widths[field] for field in constrained},
        compiled=False,
    )


def compiled_constraint_key(
    item: dict[str, Any], source: dict[str, Any]
) -> tuple[tuple[str, tuple[int, ...]], ...]:
    constraints = [
        constraint
        for part in item.get("encoding", {}).get("parts", [])
        for constraint in part.get("constraints", [])
    ]
    widths = {str(field["name"]): int(field["width"]) for field in source.get("fields", [])}
    constrained = {str(constraint["field"]) for constraint in constraints}
    return _constraint_domains(
        constraints,
        {field: widths[field] for field in constrained},
        compiled=True,
    )


def validate_extension_reservation_cardinality(
    meta: Any,
    release: Any,
    lock: Any,
    reservations: Any,
) -> list[str]:
    errors: list[str] = []

    def require_object(value: Any, label: str) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        errors.append(f"{label} must be a JSON object")
        return {}

    meta_object = require_object(meta, "v0.58 metadata")
    release_object = require_object(release, "v0.58 release manifest")
    lock_object = require_object(lock, "v0.58 PTO lock")
    reservation_object = require_object(
        reservations, "v0.58 extension reservation projection"
    )
    meta_cardinality = require_object(
        meta_object.get("cardinality"), "v0.58 metadata cardinality"
    )
    release_cardinality = require_object(
        release_object.get("cardinality"), "v0.58 release manifest cardinality"
    )
    lock_catalogs = require_object(
        lock_object.get("catalogs"), "v0.58 PTO lock catalogs"
    )
    reservation_catalog = require_object(
        lock_catalogs.get("extension_encoding_reservations"),
        "v0.58 PTO lock extension reservation catalog",
    )
    reservation_inventory = reservation_object.get("reservations")
    if not isinstance(reservation_inventory, list):
        errors.append("v0.58 extension reservation inventory must be a JSON array")
        reservation_inventory = []

    cardinalities = {
        "meta": meta_cardinality.get("extension_encoding_reservations"),
        "release manifest": release_cardinality.get(
            "extension_encoding_reservations"
        ),
        "PTO lock": reservation_catalog.get("count"),
        "reservation projection": reservation_object.get("reservation_count"),
        "reservation inventory": len(reservation_inventory),
    }
    if any(
        count != EXTENSION_RESERVATION_COUNT for count in cardinalities.values()
    ):
        details = ", ".join(
            f"{source}={count!r}" for source, count in cardinalities.items()
        )
        errors.append(
            "v0.58 extension reservation cardinalities must agree at "
            f"{EXTENSION_RESERVATION_COUNT}: {details}"
        )

    expected_note = (
        f"PTO publishes {EXTENSION_RESERVATION_COUNT} extension reservations"
    )
    notes = meta_object.get("notes")
    if not isinstance(notes, list) or not all(isinstance(note, str) for note in notes):
        errors.append("v0.58 metadata notes must be a JSON array of strings")
        notes = []
    if not any(expected_note in note for note in notes):
        errors.append(
            "v0.58 metadata notes must state the canonical extension reservation "
            f"cardinality ({EXTENSION_RESERVATION_COUNT})"
        )
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    paths = {
        "lock": "isa/v0.58/pto-spec.lock.json",
        "tiles": "isa/v0.58/state/pto_ops.json",
        "commands": "isa/v0.58/state/pto_command_forms.json",
        "scalars": "isa/v0.58/state/pto_scalar_forms.json",
        "reservations": "isa/v0.58/state/extension_encoding_reservations.json",
        "shared": "isa/v0.58/state/shared_tile_registers.json",
        "release": "isa/v0.58/release_manifest.json",
        "meta": "isa/v0.58/meta.json",
        "spec": "isa/v0.58/linxisa-v0.58.json",
    }
    missing = [relative for relative in paths.values() if not (root / relative).is_file()]
    if missing:
        return [f"missing PTO/Linx 0.58 artifact: {relative}" for relative in missing]
    docs = {name: load(root, relative) for name, relative in paths.items()}
    lock = docs["lock"]
    errors.extend(validate_extension_reservation_cardinality(
        docs["meta"], docs["release"], lock, docs["reservations"]
    ))
    if lock.get("release") != "0.58.3" or lock.get("encoding_abi") != "pto-isa-0.58.3-mode-function-v1":
        errors.append("PTO lock has the wrong 0.58.3 release/ABI identity")
    if not GIT_OID.fullmatch(str(lock.get("source", {}).get("commit", ""))):
        errors.append("PTO lock must pin an exact source commit")
    if not GIT_OID.fullmatch(str(lock.get("source", {}).get("tree", ""))):
        errors.append("PTO lock must pin an exact source tree")
    expected_catalogs = {
        "scalar_forms": 466,
        "command_forms": 74,
        "tile_operations": 109,
        "extension_encoding_reservations": EXTENSION_RESERVATION_COUNT,
    }
    for name, count in expected_catalogs.items():
        entry = lock.get("catalogs", {}).get(name, {})
        if entry.get("count") != count or not SHA256.fullmatch(str(entry.get("sha256", ""))):
            errors.append(f"PTO lock must freeze {count} {name}")

    tiles = docs["tiles"].get("operations", [])
    expected_family_counts = Counter({"TEPL": 87, "TLSU": 10, "CUBE": 12})
    expected_engine_counts = Counter({"VEC": 31, "SFU": 56, "TLSU": 10, "CUBE": 12})
    expected_classification_counts = Counter({
        "elementwise-tile-tile": 25,
        "tile-scalar-and-immediate": 15,
        "reduce-and-expand": 28,
        "memory-and-data-movement": 9,
        "matrix-and-matrix-vector": 12,
        "layout-and-rearrangement": 7,
        "irregular-and-complex": 13,
    })
    if Counter(item.get("family") for item in tiles) != expected_family_counts:
        errors.append("tile inventory must be exactly 87 TEPL / 10 TLSU / 12 CUBE")
    if Counter(item.get("engine") for item in tiles) != expected_engine_counts:
        errors.append("tile semantic engines must be exactly 31 VEC / 56 SFU / 10 TLSU / 12 CUBE")
    if Counter(item.get("classification") for item in tiles) != expected_classification_counts:
        errors.append("tile semantic classifications differ from the canonical PTO 0.58 catalog")
    if docs["tiles"].get("engine_counts") != dict(sorted(expected_engine_counts.items())):
        errors.append("PTO operation projection must publish exact semantic engine counts")
    if docs["tiles"].get("classification_counts") != dict(sorted(expected_classification_counts.items())):
        errors.append("PTO operation projection must publish exact semantic classification counts")
    source_forms = docs["scalars"].get("forms", []) + docs["commands"].get("forms", [])
    scalar_ids = {str(form["form_id"]) for form in docs["scalars"].get("forms", [])}
    if len(source_forms) != 540:
        errors.append("PTO scalar/block form inventory must contain exactly 540 forms")
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
    if len(compiled) != 540:
        errors.append("compiled Linx profile must attach exactly 540 PTO form identities")
    if set(compiled) != set(source_ids):
        errors.append("compiled Linx PTO form identity set must equal the canonical PTO set")
    for form in source_forms:
        form_id = str(form["form_id"])
        item = compiled.get(form_id)
        if item is None:
            errors.append(f"missing compiled PTO form {form_id}")
            continue
        if (item.get("mnemonic"), item.get("asm"), item.get("length_bits"), encoding_key(item, True)) != (
            form.get("mnemonic"), form.get("asm"), form.get("length_bits"), source_encoding_key(form)
        ):
            errors.append(f"compiled PTO form differs from source: {form_id}")
        if compiled_field_key(item) != source_field_key(form):
            errors.append(f"compiled PTO fields differ from source: {form_id}")
        if item.get("pto_source_fixed_fields", []) != singleton_pto_fields(form):
            errors.append(f"compiled PTO fixed fields differ from source: {form_id}")
        if form_id in scalar_ids:
            if compiled_constraint_key(item, form) != source_constraint_key(form):
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
        if (
            item.get("mnemonic"),
            item.get("asm"),
            item.get("length_bits"),
            encoding_key(item, True),
        ) != (
            form.get("mnemonic"),
            form.get("asm"),
            form.get("length_bits"),
            source_encoding_key(form, variant["encoding"]),
        ):
            errors.append(f"compiled PTO command variant differs from source: {key}")
        if compiled_field_key(item) != source_field_key(form, variant["encoding"]):
            errors.append(f"compiled PTO command variant fields differ from source: {key}")
        if item.get("pto_source_constraints") != form.get("constraints", []):
            errors.append(f"compiled PTO command variant constraints differ from source: {key}")

    linx_only = [
        item
        for item in docs["spec"].get("instructions", [])
        if not item.get("pto_source_form_id") and not item.get("pto_source_form_variant")
    ]
    vector_form_count = sum(str(item.get("mnemonic")).startswith("V.") for item in linx_only)
    if len(linx_only) != 212 or vector_form_count != 184:
        errors.append("Linx-only delta must contain exactly 184 V.* forms and 28 reserved command forms")

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
    bstart_tepl = [item for item in docs["spec"].get("instructions", []) if item.get("mnemonic") == "BSTART.TEPL"]
    if len(bstart_tepl) != 1:
        errors.append("compiled Linx profile must contain exactly one BSTART.TEPL encoding carrier")
    else:
        carrier = bstart_tepl[0]
        if carrier.get("accepted_assembly_mnemonics") != ["BSTART.TEPL", "BSTART.VEC", "BSTART.SFU"]:
            errors.append("BSTART.TEPL must accept exactly the TEPL/VEC/SFU assembly spellings")
        if carrier.get("canonical_assembly_by_engine") != {"SFU": "BSTART.SFU", "VEC": "BSTART.VEC"}:
            errors.append("BSTART.TEPL canonical assembly must be selected by VEC/SFU semantic engine")
        if carrier.get("carrier_mnemonic") != "BSTART.TEPL":
            errors.append("BSTART.TEPL must remain the unchanged encoding carrier")
    if {"BSTART.VEC", "BSTART.SFU"} & set(compiled_by_mnemonic):
        errors.append("BSTART.VEC/SFU aliases must not create additional decode identities")
    reservations = docs["reservations"].get("reservations", [])
    reservation_by_name = {str(item.get("mnemonic")): item for item in reservations}
    if (
        len(reservations) != EXTENSION_RESERVATION_COUNT
        or len(reservation_by_name) != EXTENSION_RESERVATION_COUNT
    ):
        errors.append(
            "PTO must publish exactly "
            f"{EXTENSION_RESERVATION_COUNT} unique extension encoding reservations"
        )
    uncovered = sorted(
        str(item.get("asm") or item.get("mnemonic"))
        for item in linx_only
        if not any(reservation_covers(reservation, item) for reservation in reservations)
    )
    if uncovered:
        errors.append(f"Linx-only forms escape PTO extension reservations: {uncovered}")

    shared = docs["shared"]
    if shared.get("register_count") != 256 or shared.get("register_names", {}).get("syntax") != "S<absolute-index>":
        errors.append("Shared tile bank must expose absolute S0..S255 names")
    if shared.get("scope") != {"private_to": "core", "shared_by": "four PEs in that core"}:
        errors.append("Shared tile bank must be core-private and shared by four PEs")
    size_codes = shared.get("size_code_bytes", {})
    if size_codes.get("B.IOT") != [
        None, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536
    ]:
        errors.append("B.IOT SizeCode must map 1..10 to 128 B..64 KiB")
    if size_codes.get("B.IOS") != [
        None, 128, 256, 512, 1024, 2048, 4096, 8192,
        16384, 32768, 65536, 131072, 262144,
    ]:
        errors.append("B.IOS SizeCode must map 1..12 to 128 B..256 KiB")
    mode = shared.get("pe_mode", {})
    if (
        mode.get("owners") != ["B.IOT", "B.IOS"]
        or mode.get("width") != 3
        or mode.get("decoded_masks")
        != ["0000", "1000", "0100", "0010", "0001", "1100", "1110", "1111"]
    ):
        errors.append("Local/Shared binders must use the exact 3-bit PEMode decoder")
    gm_access = shared.get("gm_access", {})
    if (
        gm_access.get("base_selector") != "B.IOR.RegSrc0"
        or gm_access.get("row_stride_selector") != "B.IOR.RegSrc1"
        or gm_access.get("row_stride_unit") != "bytes"
        or gm_access.get("b_iot_scope") != "local-only"
    ):
        errors.append("Shared GM access must use per-PE B.IOR byte stride and Local-only B.IOT")

    retired_entries = docs["spec"].get("retired_encodings", {}).get("entries")
    if retired_entries != []:
        errors.append("v0.58 deleted scalar/block spellings must not reserve encodings")

    b_ios = [item for item in docs["spec"].get("instructions", []) if item.get("mnemonic") == "B.IOS"]
    if len(b_ios) != 1 or encoding_key(b_ios[0], True) != ((0xF00871FF, 0x00001013, 32),):
        errors.append("B.IOS must own the former B.IOD 32-bit slot exactly")
    if {"B.IOD", "BSTART.PAR", "C.B.IOS"} & set(compiled_by_mnemonic):
        errors.append("deleted PTO scalar/block spellings must not decode in Linx v0.58")

    tfma = [item for item in tiles if item.get("name") == "TFMA"]
    if len(tfma) != 1 or (tfma[0].get("mode"), tfma[0].get("function"), tfma[0].get("selector")) != (0, 28, "0x01C"):
        errors.append("TFMA must remain active at TEPL Mode=0 Function=28")
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
