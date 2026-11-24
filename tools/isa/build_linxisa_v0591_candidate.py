#!/usr/bin/env python3
"""Build the local release-ready LinxISA v0.59.1 revision-1 catalog."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

from build_golden import effective_pto_encoding
from build_pto_v0591_candidate import build as build_frozen_bindings
from report_encoding_space import (
    _build_instructions,
    _conflicts_by_signature,
    _extract_patterns,
    _parts_overlap,
)


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "isa/v0.58/linxisa-v0.58.json"
PROFILE = ROOT / "isa/v0.59"
OUTPUT = PROFILE / "linxisa-v0.59.json"
BINDINGS = PROFILE / "pto-v0591-candidate.json"
SCALARS = PROFILE / "state/pto_scalar_forms.json"
COMMANDS = PROFILE / "state/pto_command_forms.json"
RESERVATIONS = PROFILE / "state/extension_encoding_reservations.json"
PTO_SYSTEM_REGISTERS = PROFILE / "state/pto_system_registers.json"
LINX_EXTENSIONS = PROFILE / "state/linx_extension_forms.json"
PUBLICATION_REVISION = 1
SIGNED_BASELINE = {
    "tag": "v0.59.1",
    "commit": "d262515b55c727073997c8f4c95261909f2fe8d3",
    "catalog_sha256": "490defb827d2aecd5c63fe231467d2a3416e5ce0361b65a65f507d9fab08079c",
}

EXPECTED_LINX_EXTENSION_IDS = frozenset(
    {
        "dma_free_l_32_5af48f644596",
        "dma_free_s_32_5de9a6bba806",
        "hl_bstart_call_48_d71cee46ab50",
        "hl_bstart_fp_48_0368fb7424f4",
        "hl_bstart_fp_48_9955c1f823f6",
        "hl_bstart_fp_48_9a0544563449",
        "hl_bstart_fp_48_f074f1e2c089",
        "hl_bstart_std_48_170d04be4f7e",
        "hl_bstart_std_48_436ff4a95f39",
        "hl_bstart_std_48_4eff98193028",
        "hl_bstart_std_48_c970f578674f",
        "hl_bstart_sys_48_54ff489122fe",
        "l_bstart_fp_64_52a1fd45d908",
        "l_bstart_fp_64_59792b6f0002",
        "l_bstart_fp_64_9673fedb498b",
        "l_bstart_fp_64_b27a4726298b",
        "l_bstart_std_64_40bf385dbbff",
        "l_bstart_std_64_49b7cf990e62",
        "l_bstart_std_64_9a6081ab8f08",
        "l_bstart_std_64_ed61315d3418",
        "l_bstart_sys_64_3e3b45c148bc",
        "mcopy_dl_32_d6af61213c20",
        "mcopy_ds_32_e7a90ccbe4db",
    }
)
REMOVED_BLOCK_MNEMONICS = frozenset(
    {
        "B.TEXT",
        "BSTART.MPAR",
        "BSTART.MSEQ",
        "BSTART.VPAR",
        "BSTART.VSEQ",
        "C.BSTART.MPAR",
        "C.BSTART.MSEQ",
        "C.BSTART.VPAR",
        "C.BSTART.VSEQ",
    }
)


def load(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return document


def render(document: object) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def pattern(mask: int, match: int, width: int) -> str:
    return "".join(
        "." if not mask & (1 << bit) else "1" if match & (1 << bit) else "0"
        for bit in reversed(range(width))
    )


def compile_fields(form: dict[str, Any], parts: list[dict[str, Any]]) -> None:
    by_part: dict[int, list[dict[str, Any]]] = {
        int(part["index"]): [] for part in parts
    }
    signedness = {"encoding-defined": None, "signed": True, "unsigned": False}
    ranges = []
    offset = 0
    for part in parts:
        width = int(part["width_bits"])
        ranges.append((int(part["index"]), offset, offset + width))
        offset += width
    for field in form.get("fields", []):
        pieces_by_part: dict[int, list[dict[str, int]]] = {}
        for piece in field.get("pieces", []):
            global_lsb = int(piece["instruction_lsb"])
            width = int(piece["width"])
            locations = [
                (
                    index,
                    max(global_lsb, begin) - begin,
                    int(piece["value_lsb"]) + max(global_lsb, begin) - global_lsb,
                    min(global_lsb + width, end) - max(global_lsb, begin),
                )
                for index, begin, end in ranges
                if max(global_lsb, begin) < min(global_lsb + width, end)
            ]
            if sum(location[3] for location in locations) != width:
                raise ValueError(
                    f"{form['form_id']}: field piece is outside encoded parts"
                )
            for part_index, local_lsb, value_lsb, local_width in locations:
                value_msb = value_lsb + local_width - 1
                token = str(field["name"])
                if value_lsb != 0 or local_width != int(field["width"]):
                    token = f"{field['name']}[{value_msb}:{value_lsb}]"
                pieces_by_part.setdefault(part_index, []).append(
                    {
                        "insn_lsb": local_lsb,
                        "insn_msb": local_lsb + local_width - 1,
                        "token": token,
                        "value_lsb": value_lsb,
                        "value_msb": value_msb,
                        "width": local_width,
                    }
                )
        for part_index, pieces in pieces_by_part.items():
            by_part[part_index].append(
                {
                    "name": field["name"],
                    "pieces": sorted(pieces, key=lambda item: item["value_lsb"]),
                    "signed": signedness[field["signedness"]],
                }
            )
    for part in parts:
        part["fields"] = sorted(
            by_part[int(part["index"])], key=lambda item: item["name"]
        )


def compile_constraints(form: dict[str, Any], parts: list[dict[str, Any]]) -> None:
    widths = {
        str(field["name"]): int(field["width"]) for field in form.get("fields", [])
    }
    ranges = []
    offset = 0
    for part in parts:
        width = int(part["width_bits"])
        ranges.append((int(part["index"]), offset, offset + width))
        offset += width
    field_part = {}
    for field in form.get("fields", []):
        locations = {
            index
            for piece in field.get("pieces", [])
            for index, begin, end in ranges
            if begin <= int(piece["instruction_lsb"]) < end
        }
        if locations:
            field_part[str(field["name"])] = min(locations)
    predicates: dict[int, list[dict[str, str]]] = {}
    for constraint in form.get("constraints", []):
        field = str(constraint["field"])
        if constraint["operator"] == "one-of":
            accepted = {int(value) for value in constraint["values"]}
            if len(accepted) == 1:
                predicates.setdefault(field_part[field], []).append(
                    {"field": field, "op": "==", "value": str(next(iter(accepted)))}
                )
            else:
                rejected = sorted(set(range(1 << widths[field])) - accepted)
                predicates.setdefault(field_part[field], []).extend(
                    {"field": field, "op": "!=", "value": str(value)}
                    for value in rejected
                )
        elif constraint["operator"] == "not-equal":
            predicates.setdefault(field_part[field], []).append(
                {"field": field, "op": "!=", "value": str(constraint["value"])}
            )
        else:
            raise ValueError(
                f"{form['form_id']}: unsupported constraint operator "
                f"{constraint['operator']!r}"
            )
    for part in parts:
        part_predicates = predicates.get(int(part["index"]), [])
        if part_predicates:
            part["constraints"] = sorted(
                part_predicates, key=lambda item: (item["field"], item["value"])
            )


def compile_encoding(form: dict[str, Any]) -> list[dict[str, Any]]:
    parts = copy.deepcopy(effective_pto_encoding(form))
    compile_fields(form, parts)
    compile_constraints(form, parts)
    for part in parts:
        width = int(part["width_bits"])
        mask = int(part["mask"], 0)
        match = int(part["match"], 0)
        part["pattern"] = pattern(mask, match, width)
    return parts


def raw_parts(parts: list[dict[str, Any]], identity: str) -> list[dict[str, Any]]:
    result = []
    for part in parts:
        width = int(part["width_bits"])
        mask = int(part["mask"], 0)
        match = int(part["match"], 0)
        labels: list[tuple[str, str, int] | None] = [None] * width
        for field in part.get("fields", []):
            for piece_index, piece in enumerate(field.get("pieces", [])):
                lsb = int(piece["insn_lsb"])
                piece_width = int(piece["width"])
                label = ("field", str(field["name"]), piece_index)
                for bit in range(lsb, lsb + piece_width):
                    if labels[bit] is not None:
                        raise ValueError(
                            f"{identity}: overlapping field pieces at bit {bit}"
                        )
                    labels[bit] = label
        for bit in range(width):
            if labels[bit] is None:
                if not mask & (1 << bit):
                    raise ValueError(f"{identity}: unowned variable bit {bit}")
                labels[bit] = ("const", "", 0)

        segments = []
        msb = width - 1
        while msb >= 0:
            label = labels[msb]
            lsb = msb
            while lsb > 0 and labels[lsb - 1] == label:
                lsb -= 1
            segment_width = msb - lsb + 1
            segment: dict[str, Any] = {
                "lsb": lsb,
                "msb": msb,
                "width": segment_width,
            }
            assert label is not None
            if label[0] == "const":
                value = (match >> lsb) & ((1 << segment_width) - 1)
                segment["const"] = {"value": value, "width": segment_width}
                segment["token"] = f"{segment_width}'b{value:0{segment_width}b}"
            else:
                segment["token"] = label[1]
            segments.append(segment)
            msb = lsb - 1
        result.append({"segments": segments, "width_bits": width})
    return result


def full_scoped_instruction(
    form: dict[str, Any], base: dict[str, Any]
) -> dict[str, Any]:
    parts = compile_encoding(form)
    uid = hashlib.sha1(form["form_id"].encode("utf-8")).hexdigest()[:12]
    item = copy.deepcopy(base)
    item.update(
        {
            "id": f"pto_scoped_{form['form_id']}",
            "uid": uid,
            "mnemonic": form["mnemonic"],
            "asm": form["asm"],
            "length_bits": 64,
            "encoding_kind": form["encoding_kind"],
            "parts": raw_parts(parts, form["form_id"]),
            "encoding": {"length_bits": 64, "parts": parts},
            "pto_source_form_id": form["form_id"],
            "pto_base_form_id": form["base_form_id"],
            "pto_scope": form["scope"],
            "pto_scope_code": int(form["scope_code"]),
            "pto_source_constraints": copy.deepcopy(form.get("constraints", [])),
            "source": {
                "file": "state/pto_scalar_forms.json",
                "form_id": form["form_id"],
            },
            "implementation_status": "published-architecture-form",
            "decoder_dispatch": "scoped-sail-dispatch",
        }
    )
    return item


def check_collisions(document: dict[str, Any]) -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "candidate.json"
        path.write_text(render(document), encoding="utf-8")
        instructions = _build_instructions(_extract_patterns(path))
    conflicts = [
        (left.inst_id, right.inst_id)
        for pairs in _conflicts_by_signature(instructions).values()
        for left, right in pairs
    ]
    single32 = [
        item
        for item in instructions
        if len(item.parts) == 1 and item.parts[0].width_bits == 32
    ]
    prefixes = [
        item
        for item in instructions
        if len(item.parts) > 1 and item.parts[0].width_bits == 32
    ]
    prefix_conflicts = [
        (multi.inst_id, single.inst_id)
        for multi in prefixes
        for single in single32
        if _parts_overlap(multi.parts[0], single.parts[0])
    ]
    if conflicts or prefix_conflicts:
        examples = [*conflicts[:3], *prefix_conflicts[:3]]
        raise ValueError(f"candidate encoding collisions: {examples}")


def complete_field_definitions(document: dict[str, Any]) -> None:
    observed: dict[str, dict[str, set[Any]]] = {}
    for item in document["instructions"]:
        for part in item["encoding"]["parts"]:
            for field in part.get("fields", []):
                entry = observed.setdefault(
                    str(field["name"]), {"widths": set(), "signed": set()}
                )
                entry["widths"].add(
                    sum(int(piece["width"]) for piece in field.get("pieces", []))
                )
                if field.get("signed") is not None:
                    entry["signed"].add(bool(field["signed"]))

    source_definitions = document["field_definitions"]["fields"]
    definitions = {
        name: copy.deepcopy(definition)
        for name, definition in source_definitions.items()
        if name in observed or definition.get("documented_only") is True
    }
    document["field_definitions"]["fields"] = definitions
    for name, entry in observed.items():
        definition = definitions.get(name)
        if definition is None:
            if name == "Reserved":
                definition = {
                    "namespace": "reserved",
                    "allowed_values": [0],
                }
            else:
                definition = {
                    "namespace": "selector",
                    "reserved_values": [3]
                    if name in {"InnerLength", "Shareability"}
                    else [],
                }
            definitions[name] = definition
        definition["widths"] = sorted(entry["widths"])
        if len(entry["signed"]) == 1:
            definition["signed"] = next(iter(entry["signed"]))


def frozen_bindings() -> tuple[dict[str, Any], str]:
    rebuilt = build_frozen_bindings()
    rebuilt_text = render(rebuilt)
    on_disk = BINDINGS.read_text(encoding="utf-8")
    if on_disk != rebuilt_text:
        raise ValueError("on-disk PTO v0.59.1 bindings differ from rebuilt bindings")
    return rebuilt, hashlib.sha256(rebuilt_text.encode("utf-8")).hexdigest()


def linx_extension_forms() -> list[dict[str, Any]]:
    document = load(LINX_EXTENSIONS)
    if document.get("version") != "0.59.1":
        raise ValueError("Linx extension source must describe v0.59.1")
    if document.get("status") != "release-ready":
        raise ValueError("Linx extension source is not release-ready")
    forms = document.get("forms")
    if not isinstance(forms, list):
        raise ValueError("Linx extension source forms must be an array")
    form_ids = [form.get("id") for form in forms]
    if (
        document.get("form_count") != 23
        or document.get("form_ids") != form_ids
        or len(form_ids) != len(set(form_ids))
        or set(form_ids) != EXPECTED_LINX_EXTENSION_IDS
    ):
        raise ValueError(
            "Linx extension source must contain exactly the 23 retained forms"
        )
    if any(form.get("pto_source_form_id") for form in forms):
        raise ValueError("Linx extension source contains a PTO-owned form")
    if any(
        str(form.get("mnemonic", "")).startswith("V.")
        or form.get("mnemonic") in REMOVED_BLOCK_MNEMONICS
        for form in forms
    ):
        raise ValueError("Linx extension source contains a removed execution form")
    return copy.deepcopy(forms)


def build() -> dict[str, Any]:
    baseline = load(BASELINE)
    scalar = load(SCALARS)
    command = load(COMMANDS)
    frozen, bindings_sha256 = frozen_bindings()
    source_forms = [*scalar["forms"], *command["forms"]]
    source = {form["form_id"]: form for form in source_forms}
    baseline_common = {
        item["pto_source_form_id"]: item
        for item in baseline["instructions"]
        if item.get("pto_source_form_id")
    }
    frozen_common = {
        item["pto_source_form_id"]: item for item in frozen["common_bindings"]
    }
    if not (
        len(source) == len(baseline_common) == len(frozen_common) == 578
        and source.keys() == baseline_common.keys() == frozen_common.keys()
    ):
        raise ValueError(
            "578 released common identities do not map one-to-one to v0.58"
        )

    common = []
    for identity in sorted(source):
        form = source[identity]
        prior = baseline_common[identity]
        binding = frozen_common[identity]
        if (prior["id"], prior["uid"]) != (binding["linx_id"], binding["linx_uid"]):
            raise ValueError(f"{identity}: frozen binding changed its v0.58 identity")
        parts = compile_encoding(form)
        item = copy.deepcopy(prior)
        item.update(
            {
                "mnemonic": form["mnemonic"],
                "asm": form["asm"],
                "length_bits": int(form["length_bits"]),
                "encoding_kind": form["encoding_kind"],
                "parts": raw_parts(parts, identity),
                "encoding": {"length_bits": int(form["length_bits"]), "parts": parts},
                "pto_source_constraints": copy.deepcopy(form.get("constraints", [])),
            }
        )
        common.append(item)

    linx_only = linx_extension_forms()

    scoped_source = {form["form_id"]: form for form in scalar["scoped_forms"]}
    frozen_scoped = {
        item["pto_source_form_id"]: item for item in frozen["scoped_bindings"]
    }
    if not (
        len(scoped_source) == len(frozen_scoped) == 705
        and scoped_source.keys() == frozen_scoped.keys()
    ):
        raise ValueError("705 released scoped identities do not match frozen bindings")
    scoped = []
    for identity in sorted(scoped_source):
        form = scoped_source[identity]
        base = baseline_common.get(form["base_form_id"])
        if base is None:
            raise ValueError(
                f"{identity}: missing v0.58 base binding {form['base_form_id']}"
            )
        scoped.append(full_scoped_instruction(form, base))

    instructions = sorted(
        [*common, *linx_only, *scoped],
        key=lambda item: (
            str(item.get("mnemonic")),
            int(item.get("length_bits", 0)),
            str(item.get("id")),
        ),
    )
    ids = [item["id"] for item in instructions]
    uids = [item["uid"] for item in instructions]
    if len(ids) != len(set(ids)) or len(uids) != len(set(uids)):
        raise ValueError("candidate instruction IDs or UIDs collide")

    state = {
        "pto_scalar_forms": copy.deepcopy(scalar),
        "pto_command_forms": copy.deepcopy(command),
        "extension_encoding_reservations": load(RESERVATIONS),
        "pto_system_registers": load(PTO_SYSTEM_REGISTERS),
    }
    semantics_conventions = copy.deepcopy(baseline["semantics_conventions"])
    semantics_conventions.pop("block_legality", None)
    semantics_conventions.pop("extension_first_use", None)
    document = {
        "schema": baseline["schema"],
        "isa": baseline["isa"],
        "version": "0.59.1",
        "release_status": {
            "state": "local-release-ready",
            "publication_revision": PUBLICATION_REVISION,
            "signed_baseline": copy.deepcopy(SIGNED_BASELINE),
            "selection": "explicit-v0.59-profile",
            "default_profile": "v0.58",
            "publication_allowed": True,
            "release_qualified": True,
            "qualification_scope": [
                "source",
                "architecture-specification",
                "encoding",
                "sail-package",
            ],
            "platform_qualified": False,
            "source_bindings": "isa/v0.59/pto-v0591-candidate.json",
            "source_bindings_sha256": bindings_sha256,
            "counts": {"common": 578, "linx_only": 23, "scoped": 705},
            "authoritative_v059_paths": [
                "instructions",
                "state.pto_scalar_forms",
                "state.pto_command_forms",
                "state.extension_encoding_reservations",
                "state.pto_system_registers",
            ],
            "external_authoritative_v059_files": {
                "tile_operations": {
                    "path": "isa/v0.59/state/pto_tile_operations.json",
                    "precedence": "authoritative-v0.59-owner",
                },
                "hardware_conformance_profile": {
                    "path": "isa/v0.59/state/pto_hardware_conformance_profile.json"
                },
                "numeric_conformance_vectors": {
                    "path": "isa/v0.59/state/pto_hardware_numeric_vectors.json"
                },
            },
            "linx_extension_source": {
                "status": "v0.59-owned-positive-definitions",
                "path": "isa/v0.59/state/linx_extension_forms.json",
                "row_count": 23,
                "verification": "exact-row-identity-with-v0.59.1-reference-tag",
            },
        },
        "instruction_count": len(instructions),
        "instructions": instructions,
        "registers": copy.deepcopy(baseline["registers"]),
        "field_definitions": copy.deepcopy(baseline["field_definitions"]),
        "semantics_conventions": semantics_conventions,
        "retired_encodings": copy.deepcopy(baseline["retired_encodings"]),
        "state": state,
    }
    complete_field_definitions(document)
    if document["instruction_count"] != 1306:
        raise ValueError(f"expected 1306 working rows, found {len(instructions)}")
    check_collisions(document)
    return document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        expected = render(build())
    except (KeyError, OSError, ValueError) as error:
        raise SystemExit(f"LinxISA v0.59.1 candidate build failed: {error}") from error
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"stale LinxISA v0.59.1 catalog: {OUTPUT}")
        print(f"LinxISA v0.59.1 catalog is current: {OUTPUT}")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
