#!/usr/bin/env python3
"""Build an inactive Linx catalog candidate for the released PTO ISA 0.59.1."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from build_golden import effective_pto_encoding


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "isa/v0.58/linxisa-v0.58.json"
PROFILE = ROOT / "isa/v0.59"
OUTPUT = PROFILE / "pto-v0591-candidate.json"
SCALARS = PROFILE / "state/pto_scalar_forms.json"
COMMANDS = PROFILE / "state/pto_command_forms.json"
LOCK = PROFILE / "pto-spec.lock.json"


def load(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return document


def render(document: object) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def digest(document: object) -> str:
    return hashlib.sha256(
        json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def compiled_fields(form: dict[str, Any], parts: list[dict[str, Any]]) -> None:
    by_part: dict[int, list[dict[str, Any]]] = {
        int(part["index"]): [] for part in parts
    }
    signedness = {"encoding-defined": None, "signed": True, "unsigned": False}
    for field in form.get("fields", []):
        pieces_by_part: dict[int, list[dict[str, int]]] = {}
        for piece in field.get("pieces", []):
            global_lsb = int(piece["instruction_lsb"])
            part_index, local_lsb = divmod(global_lsb, 32)
            pieces_by_part.setdefault(part_index, []).append(
                {
                    "insn_lsb": local_lsb,
                    "value_lsb": int(piece["value_lsb"]),
                    "width": int(piece["width"]),
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


def compiled_constraints(form: dict[str, Any], parts: list[dict[str, Any]]) -> None:
    widths = {
        str(field["name"]): int(field["width"]) for field in form.get("fields", [])
    }
    fields = {str(field["name"]): field for field in form.get("fields", [])}
    global_mask = offset = 0
    for part in parts:
        global_mask |= int(part["mask"], 0) << offset
        offset += int(part["width_bits"])

    def is_variable(field: str) -> bool:
        for piece in fields[field].get("pieces", []):
            piece_mask = ((1 << int(piece["width"])) - 1) << int(
                piece["instruction_lsb"]
            )
            if global_mask & piece_mask != piece_mask:
                return True
        return False

    predicates = []
    for constraint in form.get("constraints", []):
        field = str(constraint["field"])
        if not is_variable(field):
            continue
        if constraint["operator"] == "one-of":
            accepted = {int(value) for value in constraint["values"]}
            predicates.extend(
                {"field": field, "op": "!=", "value": str(value)}
                for value in sorted(set(range(1 << widths[field])) - accepted)
            )
        elif constraint["operator"] == "not-equal":
            predicates.append(
                {"field": field, "op": "!=", "value": str(constraint["value"])}
            )
        else:
            raise ValueError(
                f"{form['form_id']}: unsupported constraint operator "
                f"{constraint['operator']!r}"
            )
    if predicates:
        parts[0]["constraints"] = predicates


def scoped_instruction(form: dict[str, Any]) -> dict[str, Any]:
    parts = copy.deepcopy(effective_pto_encoding(form))
    compiled_fields(form, parts)
    compiled_constraints(form, parts)
    return {
        "candidate_id": f"pto-scoped::{form['form_id']}",
        "candidate_uid": hashlib.sha1(form["form_id"].encode("utf-8")).hexdigest()[:12],
        "mnemonic": form["mnemonic"],
        "asm": form["asm"],
        "length_bits": 64,
        "encoding_kind": form["encoding_kind"],
        "compiled_encoding": parts,
        "pto_source_form_id": form["form_id"],
        "pto_base_form_id": form["base_form_id"],
        "pto_scope": form["scope"],
        "pto_scope_code": int(form["scope_code"]),
        "implementation_status": "inactive-decode-contract-only",
        # Exact operands, constraints and handler identity remain singular in
        # the locked source row named by pto_source_form_id.
        "pto_source_path": "isa/v0.59/state/pto_scalar_forms.json",
    }


def build() -> dict[str, Any]:
    baseline = load(BASELINE)
    scalars = load(SCALARS)
    commands = load(COMMANDS)
    lock = load(LOCK)
    common_rows = [*scalars["forms"], *commands["forms"]]
    common = {row["form_id"]: row for row in common_rows}
    bound = {
        item["pto_source_form_id"]: item
        for item in baseline["instructions"]
        if item.get("pto_source_form_id")
    }
    if len(common) != 578 or bound.keys() != common.keys():
        raise ValueError("active Linx common bindings do not equal the released PTO forms")
    common_bindings = []
    for identity in sorted(common):
        form = common[identity]
        item = copy.deepcopy(bound[identity])
        for part in item["encoding"]["parts"]:
            part.pop("constraints", None)
        compiled_constraints(form, item["encoding"]["parts"])
        common_bindings.append(
            {
                "linx_id": item["id"],
                "linx_uid": item["uid"],
                "pto_source_form_id": identity,
                "mnemonic": form["mnemonic"],
                "asm": form["asm"],
                "length_bits": int(form["length_bits"]),
                "compiled_encoding": item["encoding"]["parts"],
                "source_constraints": copy.deepcopy(form["constraints"]),
                "source_path": (
                    "isa/v0.59/state/pto_scalar_forms.json"
                    if identity in {row["form_id"] for row in scalars["forms"]}
                    else "isa/v0.59/state/pto_command_forms.json"
                ),
            }
        )

    scoped_rows = scalars["scoped_forms"]
    if len(scoped_rows) != 705 or len({row["form_id"] for row in scoped_rows}) != 705:
        raise ValueError("released scoped Scalar inventory is not exactly 705 unique forms")
    scoped_bindings = [scoped_instruction(row) for row in scoped_rows]
    if len({row["candidate_id"] for row in scoped_bindings}) != 705 or len(
        {row["candidate_uid"] for row in scoped_bindings}
    ) != 705:
        raise ValueError("scoped candidate identities are not globally unique")
    linx_only = [
        item for item in baseline["instructions"] if not item.get("pto_source_form_id")
    ]
    return {
        "schema": "linxisa.pto-v0591-candidate.v1",
        "version": "0.59.1",
        "release_status": {
        "state": "published-frozen-bindings",
        "selection": "explicit-v0.59-profile",
        "source_lock": "isa/v0.59/pto-spec.lock.json",
        "pto_release": lock["release"],
        "publication": lock["publication"],
        "encoding_abi": lock["encoding_abi"],
        "encoding_projection_sha256": lock["encoding_projection_sha256"],
        "scope": (
            "Published LinxISA 0.59.1 specification bindings. Platform, QEMU, "
            "Linux, RTL, and leaf-component adoption remain separate gates."
        ),
        },
        "baseline": {
            "path": "isa/v0.58/linxisa-v0.58.json",
            "version": baseline["version"],
            "instruction_count": baseline["instruction_count"],
            "sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
            "linx_only_count": len(linx_only),
            "linx_only_sha256": digest(linx_only),
        },
        "counts": {
            "common_bindings": len(common_bindings),
            "scoped_bindings": len(scoped_bindings),
        },
        "common_bindings": common_bindings,
        "scoped_bindings": scoped_bindings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        expected = render(build())
    except (KeyError, OSError, ValueError) as error:
        raise SystemExit(f"PTO v0.59.1 candidate build failed: {error}") from error
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"stale PTO v0.59.1 candidate: {OUTPUT}")
        print(f"PTO v0.59.1 candidate is current: {OUTPUT}")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
