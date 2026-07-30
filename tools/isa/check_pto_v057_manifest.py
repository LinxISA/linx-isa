#!/usr/bin/env python3
"""Validate the locked PTO ISA 0.57.1 projections and compiled command ABI."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RELEASE = "0.57.1"
ABI = "pto-isa-0.57.1-mode-function-v1"
LOCK_REF = "isa/v0.57/pto-spec.lock.json"
HASH = re.compile(r"^[0-9a-f]{64}$")
ALIASES = {"TTRANSPOSE": "TTRANS", "TSORT32": "TSORT"}
RETIRED_COMMAND_MNEMONICS = {"B.ARG", "BSTART.CUBE", "BSTART.FIXP"}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _piece_signature(fields: list[dict[str, Any]], compiled: bool) -> dict[str, tuple[tuple[int, int], ...]]:
    grouped: dict[str, list[tuple[int, int]]] = {}
    for field in fields:
        pieces = field.get("pieces", [])
        if compiled:
            value = [(int(piece["insn_lsb"]), int(piece["width"])) for piece in pieces]
        else:
            value = [(int(piece["instruction_lsb"]), int(piece["width"])) for piece in pieces]
        grouped.setdefault(str(field["name"]), []).extend(value)
    return {name: tuple(sorted(pieces)) for name, pieces in grouped.items()}


def _constraints_match(form: dict[str, Any], item: dict[str, Any]) -> bool:
    widths = {str(field["name"]): int(field["width"]) for field in form.get("fields", [])}
    expected: dict[str, set[int]] = {}
    for constraint in form.get("constraints", []):
        field = str(constraint["field"])
        domain = set(range(1 << widths[field]))
        if constraint["operator"] == "one-of":
            allowed = {int(value) for value in constraint["values"]}
        elif constraint["operator"] == "not-equal":
            allowed = domain - {int(constraint["value"])}
        else:
            raise ValueError(f"unsupported PTO constraint operator {constraint['operator']!r}")
        expected[field] = expected.get(field, domain) & allowed

    actual: dict[str, set[int]] = {}
    for part in item.get("encoding", {}).get("parts", []):
        for constraint in part.get("constraints", []) or []:
            field = str(constraint["field"])
            if field not in widths or constraint.get("op") != "!=":
                raise ValueError(f"unsupported compiled constraint for {form['form_id']}: {constraint!r}")
            domain = set(range(1 << widths[field]))
            actual.setdefault(field, domain).discard(int(str(constraint["value"]), 0))
    normalized_expected = {name: tuple(sorted(values)) for name, values in expected.items()}
    normalized_actual = {name: tuple(sorted(values)) for name, values in actual.items()}
    return normalized_actual == normalized_expected


def _validate_compiled_forms(root: Path, source: dict[str, Any], errors: list[str]) -> None:
    spec_path = root / "isa/v0.57/linxisa-v0.57.json"
    if not spec_path.is_file():
        errors.append(f"missing compiled spec: {spec_path}")
        return
    spec = _load(spec_path)
    compiled = {
        str(item["pto_source_form_id"]): item
        for item in spec.get("instructions", [])
        if item.get("pto_source_form_id")
    }
    for form in source["forms"]:
        form_id = str(form["form_id"])
        item = compiled.get(form_id)
        if item is None:
            errors.append(f"compiled command form missing source identity {form_id}")
            continue
        if item.get("mnemonic") != form.get("mnemonic") or item.get("length_bits") != form.get("length_bits"):
            errors.append(f"{form_id}: mnemonic/length differs from PTO source")
        actual_encoding = [
            (int(part["mask"], 0), int(part["match"], 0), int(part["width_bits"]))
            for part in item.get("encoding", {}).get("parts", [])
        ]
        expected_encoding = [
            (int(part["mask"], 0), int(part["match"], 0), int(part["width_bits"]))
            for part in form.get("encoding", [])
        ]
        if actual_encoding != expected_encoding:
            errors.append(f"{form_id}: mask/match differs from PTO source")
        actual_fields = []
        instruction_offset = 0
        for part in item.get("encoding", {}).get("parts", []):
            for field in part.get("fields", []):
                actual_fields.append({
                    "name": field["name"],
                    "pieces": [
                        {**piece, "insn_lsb": int(piece["insn_lsb"]) + instruction_offset}
                        for piece in field.get("pieces", [])
                    ],
                })
            instruction_offset += int(part["width_bits"])
        if _piece_signature(actual_fields, True) != _piece_signature(form.get("fields", []), False):
            errors.append(f"{form_id}: field layout differs from PTO source")
        if not _constraints_match(form, item):
            errors.append(f"{form_id}: legality constraints differ from PTO source")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    profile = root / "isa/v0.57"
    paths = {
        "lock": profile / "pto-spec.lock.json",
        "operations": profile / "state/pto_ops.json",
        "encoding": profile / "state/pto_encoding_map.json",
        "commands": profile / "state/pto_command_forms.json",
        "engine": profile / "state/engine_ops.json",
        "release": profile / "release_manifest.json",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        return [f"missing PTO 0.57.1 projection: {path}" for path in missing]
    documents = {name: _load(path) for name, path in paths.items()}
    lock = documents["lock"]
    if lock.get("release") != RELEASE or lock.get("encoding_abi") != ABI:
        errors.append("pto-spec lock has the wrong release or encoding ABI")
    for label, value in (
        ("content_sha256", lock.get("content_sha256")),
        ("encoding_projection_sha256", lock.get("encoding_projection_sha256")),
        ("release manifest hash", lock.get("release_manifest", {}).get("sha256")),
        ("tile catalog hash", lock.get("catalogs", {}).get("tile_operations", {}).get("sha256")),
        ("command catalog hash", lock.get("catalogs", {}).get("command_forms", {}).get("sha256")),
    ):
        if not isinstance(value, str) or HASH.fullmatch(value) is None:
            errors.append(f"pto-spec lock {label} is not a SHA-256")
    if lock.get("catalogs", {}).get("tile_operations", {}).get("count") != 120:
        errors.append("pto-spec lock must freeze exactly 120 tile operations")
    if lock.get("catalogs", {}).get("command_forms", {}).get("count") != 99:
        errors.append("pto-spec lock must freeze exactly 99 command forms")

    for name in ("operations", "encoding", "commands", "engine", "release"):
        document = documents[name]
        if name != "commands" and document.get("version") != RELEASE:
            errors.append(f"{name}: version must be {RELEASE}")
        if document.get("source_lock") != LOCK_REF:
            errors.append(f"{name}: source_lock must be {LOCK_REF}")

    operations = documents["operations"].get("operations", [])
    entries = documents["encoding"].get("entries", [])
    engine = documents["engine"]
    if len(operations) != 120 or len(entries) != 120:
        errors.append("PTO tile projections must contain exactly 120 entries")
        return errors
    counts = Counter(str(item.get("family")) for item in operations)
    if counts != Counter({"TEPL": 98, "TMA": 9, "CUBE": 13}):
        errors.append(f"tile family counts differ from 98/9/13: {dict(counts)}")
    names = [str(item.get("name")) for item in operations]
    if len(names) != len(set(names)):
        errors.append("PTO tile operation names are not unique")
    if any(item.get("contract_status") != "reviewed-complete" for item in operations):
        errors.append("all 120 tile contracts must be reviewed-complete")
    deleted = set(documents["operations"].get("deleted_names", []))
    rejected = set(documents["operations"].get("rejected_names", []))
    leaked = sorted((deleted | rejected | set(ALIASES)) & set(names))
    if leaked:
        errors.append(f"deleted/rejected/migration-only names leaked into tile operations: {leaked}")
    if documents["encoding"].get("migration_aliases") != ALIASES:
        errors.append("encoding migration aliases must be exactly TTRANSPOSE/TTRANS and TSORT32/TSORT")
    if documents["encoding"].get("policy", {}).get("legacy_decode_allowed") is not False:
        errors.append("legacy PTO decodes must be disabled")

    tepl = [item for item in operations if item.get("family") == "TEPL"]
    selectors = []
    for item in tepl:
        expected = (int(item["mode"]) << 5) | int(item["function"])
        if int(str(item["selector"]), 0) != expected:
            errors.append(f"{item.get('name')}: selector is not (Mode<<5)|Function")
        selectors.append(expected)
    if len(set(selectors)) != 98:
        errors.append("TEPL Mode/Function assignments are not 98 unique selectors")
    engine_tepl = {
        item["name"]: (item.get("mode"), item.get("function"), item.get("logical_selector"))
        for item in engine.get("tepl", {}).get("ops", [])
    }
    expected_tepl = {
        item["name"]: (item["mode"], item["function"], int(str(item["selector"]), 0))
        for item in tepl
    }
    if engine.get("tepl", {}).get("kind") != "mode_function" or engine_tepl != expected_tepl:
        errors.append("engine TEPL projection differs from the 98-operation source map")
    tma_functions = {int(item["function"]) for item in operations if item.get("family") == "TMA"}
    cube_functions = {int(item["function"]) for item in operations if item.get("family") == "CUBE"}
    if tma_functions != set(range(9)):
        errors.append("TMA functions must be exactly 0..8")
    if cube_functions != {0, 1, 2, 4, 5, 6, 8, 16, 17, 18, 20, 21, 22}:
        errors.append("CUBE functions differ from the 13 named source operations")
    if engine.get("cube", {}).get("unassigned_function_behavior") != "illegal_instruction":
        errors.append("unassigned CUBE functions must trap as illegal instructions")

    commands = documents["commands"]
    forms = commands.get("forms", [])
    if commands.get("form_count") != 99 or len(forms) != 99:
        errors.append("PTO command source must contain exactly 99 forms")
    families = Counter(str(item.get("semantic_family")) for item in forms)
    if families != Counter({"CMD": 74, "BBD": 25}):
        errors.append(f"command source families differ from 74 CMD / 25 BBD: {dict(families)}")
    _validate_compiled_forms(root, commands, errors)
    compiled_mnemonics = {str(item.get("mnemonic")) for item in _load(
        root / "isa/v0.57/linxisa-v0.57.json").get("instructions", [])}
    retired_leaks = sorted(RETIRED_COMMAND_MNEMONICS & compiled_mnemonics)
    if retired_leaks:
        errors.append(f"retired PTO command forms remain executable: {retired_leaks}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
