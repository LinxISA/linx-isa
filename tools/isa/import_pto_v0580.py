#!/usr/bin/env python3
"""Import the canonical PTO ISA 0.58.5 release into the Linx v0.58 profile."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "isa" / "v0.58"
LOCK_PATH = PROFILE / "pto-spec.lock.json"
RELEASE = "0.58.5"
EXPECTED_ABI = "pto-isa-0.58.5-mode-function-v1"
VECTOR_BASENAME = "pto-isa-0585-hardware-numeric-vectors.json"
SCALAR_FORM_COUNT = 466
COMMAND_FORM_COUNT = 76
TILE_OPERATION_COUNT = 108
EXTENSION_RESERVATION_COUNT = 46


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pretty(document: Any) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def source_paths(source_root: Path) -> dict[str, Path]:
    return {
        "manifest": source_root / "spec/release-manifest.json",
        "tiles": source_root / "spec/catalog/tile-operations.json",
        "commands": source_root / "spec/catalog/command-forms.json",
        "scalars": source_root / "spec/catalog/scalar-forms.json",
        "reservations": source_root / "spec/catalog/extension-encoding-reservations.json",
        "hardware": source_root / "spec/hardware-conformance-profile.json",
        "vectors": source_root / "spec/evidence" / VECTOR_BASENAME,
    }


def validate_source(source_root: Path) -> dict[str, dict[str, Any]]:
    paths = source_paths(source_root)
    for path in paths.values():
        if not path.is_file():
            raise ValueError(f"missing upstream PTO source: {path}")
    docs = {name: load_json(path) for name, path in paths.items()}
    manifest = docs["manifest"]
    if manifest.get("release") != RELEASE or manifest.get("encoding_abi") != EXPECTED_ABI:
        raise ValueError("upstream PTO release/encoding ABI is not the canonical 0.58.5 contract")
    counts = manifest.get("catalog_counts") or {}
    expected = {
        "tile_operations_total": TILE_OPERATION_COUNT,
        "command_forms": COMMAND_FORM_COUNT,
        "scalar_forms": SCALAR_FORM_COUNT,
        "extension_encoding_reservations": EXTENSION_RESERVATION_COUNT,
    }
    if any(counts.get(key) != value for key, value in expected.items()):
        raise ValueError(f"unexpected PTO 0.58 catalog counts: {counts}")
    if Counter(item["family"] for item in docs["tiles"]["operations"]) != Counter(
        {"TEPL": 86, "TLSU": 10, "CUBE": 12}
    ):
        raise ValueError("unexpected PTO 0.58 tile family counts")
    if Counter(item["engine"] for item in docs["tiles"]["operations"]) != Counter(
        {"VEC": 31, "SFU": 55, "TLSU": 10, "CUBE": 12}
    ):
        raise ValueError("unexpected PTO 0.58 semantic engine counts")
    if Counter(item["classification"] for item in docs["tiles"]["operations"]) != Counter(
        {
            "elementwise-tile-tile": 25,
            "tile-scalar-and-immediate": 15,
            "reduce-and-expand": 28,
            "memory-and-data-movement": 9,
            "matrix-and-matrix-vector": 12,
            "layout-and-rearrangement": 10,
            "irregular-and-complex": 9,
        }
    ):
        raise ValueError("unexpected PTO 0.58 tile classification counts")
    if Counter(item["semantic_family"] for item in docs["commands"]["forms"]) != Counter(
        {"CMD": 71, "BBD": 5}
    ):
        raise ValueError("unexpected PTO 0.58 command family counts")
    if (
        docs["scalars"].get("form_count") != SCALAR_FORM_COUNT
        or docs["reservations"].get("reservation_count")
        != EXTENSION_RESERVATION_COUNT
    ):
        raise ValueError("unexpected PTO 0.58 scalar/reservation cardinality")

    canonical = {entry["path"]: entry["sha256"] for entry in manifest["canonical_inputs"]}
    for name, relative in {
        "tiles": "spec/catalog/tile-operations.json",
        "commands": "spec/catalog/command-forms.json",
        "scalars": "spec/catalog/scalar-forms.json",
        "reservations": "spec/catalog/extension-encoding-reservations.json",
    }.items():
        if canonical.get(relative) != sha256(paths[name]):
            raise ValueError(f"{relative} does not match the release manifest")
    hardware = manifest["hardware_conformance_profile"]
    if hardware.get("evidence") != f"spec/evidence/{VECTOR_BASENAME}":
        raise ValueError("release manifest names the wrong numeric evidence")
    if hardware.get("sha256") != sha256(paths["hardware"]):
        raise ValueError("hardware profile does not match the release manifest")
    if docs["vectors"].get("hardware_profile_id") != docs["hardware"].get("profile_id"):
        raise ValueError("numeric vectors target another hardware profile")
    return docs


def build_lock(source_root: Path, docs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    paths = source_paths(source_root)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source_root, text=True).strip()
        tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=source_root, text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"cannot resolve upstream git identity: {exc}") from exc
    manifest = docs["manifest"]
    catalogs = {}
    for name, relative, count in (
        ("command_forms", "spec/catalog/command-forms.json", COMMAND_FORM_COUNT),
        ("scalar_forms", "spec/catalog/scalar-forms.json", SCALAR_FORM_COUNT),
        ("tile_operations", "spec/catalog/tile-operations.json", TILE_OPERATION_COUNT),
        (
            "extension_encoding_reservations",
            "spec/catalog/extension-encoding-reservations.json",
            EXTENSION_RESERVATION_COUNT,
        ),
    ):
        key = "reservations" if name == "extension_encoding_reservations" else name.split("_")[0] + "s"
        catalogs[name] = {"path": relative, "sha256": sha256(paths[key]), "count": count}
    return {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/pto_spec_lock.v1.json",
        "catalogs": catalogs,
        "content_sha256": manifest["content_sha256"],
        "encoding_abi": manifest["encoding_abi"],
        "encoding_projection_sha256": manifest["encoding_projection_sha256"],
        "hardware_conformance_profile": {
            "path": "spec/hardware-conformance-profile.json",
            "profile_id": manifest["hardware_conformance_profile"]["profile_id"],
            "sha256": sha256(paths["hardware"]),
        },
        "numeric_conformance_vectors": {
            "path": f"spec/evidence/{VECTOR_BASENAME}",
            "sha256": sha256(paths["vectors"]),
        },
        "release": RELEASE,
        "release_manifest": {"path": "spec/release-manifest.json", "sha256": sha256(paths["manifest"])},
        "source": {
            "commit": commit,
            "tree": tree,
            "repository": "https://github.com/PTO-ISA/pto-spec.git",
        },
    }


def locked_projection(document: dict[str, Any]) -> dict[str, Any]:
    result = dict(document)
    result["source_lock"] = "isa/v0.58/pto-spec.lock.json"
    return result


def project_pto_ops(tiles: dict[str, Any]) -> dict[str, Any]:
    family_counts = Counter(operation["family"] for operation in tiles["operations"])
    engine_counts = Counter(operation["engine"] for operation in tiles["operations"])
    classification_counts = Counter(operation["classification"] for operation in tiles["operations"])
    return {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/pto_ops.v1.json",
        "profile": "v0.58",
        "version": RELEASE,
        "source_lock": "isa/v0.58/pto-spec.lock.json",
        "operation_count": len(tiles["operations"]),
        "family_counts": dict(sorted(family_counts.items())),
        "engine_counts": dict(sorted(engine_counts.items())),
        "classification_counts": dict(sorted(classification_counts.items())),
        "deleted_names": tiles["deleted_names"],
        "rejected_names": tiles["rejected_names"],
        "reserved": tiles["reserved"],
        "operations": tiles["operations"],
    }


def project_encoding_map(tiles: dict[str, Any]) -> dict[str, Any]:
    entries = [
        {key: operation.get(key) for key in (
            "name", "family", "classification", "engine", "command_mnemonic",
            "selector", "mode", "function", "disposition", "contract_status"
        )}
        for operation in tiles["operations"]
    ]
    return {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/pto_encoding_map.v1.json",
        "profile": "v0.58",
        "version": RELEASE,
        "source_lock": "isa/v0.58/pto-spec.lock.json",
        "policy": {
            "catalog_order_allocates_encodings": False,
            "unlisted_selectors_reserved": True,
            "legacy_decode_allowed": False,
            "source_aliases_are_migration_only": False,
        },
        "entry_count": len(entries),
        "family_counts": dict(sorted(Counter(entry["family"] for entry in entries).items())),
        "engine_counts": dict(sorted(Counter(entry["engine"] for entry in entries).items())),
        "classification_counts": dict(
            sorted(Counter(entry["classification"] for entry in entries).items())
        ),
        "migration_aliases": {},
        "entries": entries,
    }


def project_release_manifest(docs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    manifest, tiles, commands, scalars = (docs[name] for name in ("manifest", "tiles", "commands", "scalars"))
    return {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/release_manifest.v1.json",
        "profile": "v0.58",
        "version": RELEASE,
        "source_lock": "isa/v0.58/pto-spec.lock.json",
        "policy": {
            "pto_spec_is_sole_source_for_scalar_block": True,
            "linx_vector_extension_is_additive": True,
            "legacy_decode_allowed": False,
            "unlisted_selectors_reserved": True,
        },
        "cardinality": {
            "tile_operations": len(tiles["operations"]),
            "tile_families": dict(sorted(Counter(item["family"] for item in tiles["operations"]).items())),
            "semantic_engines": dict(sorted(Counter(item["engine"] for item in tiles["operations"]).items())),
            "tile_classifications": dict(
                sorted(Counter(item["classification"] for item in tiles["operations"]).items())
            ),
            "command_forms": len(commands["forms"]),
            "command_form_families": manifest["catalog_counts"]["command_form_families"],
            "scalar_forms": len(scalars["forms"]),
            "extension_encoding_reservations": EXTENSION_RESERVATION_COUNT,
        },
        "migration_aliases": {},
        "deleted_names": tiles["deleted_names"],
        "rejected_names": tiles["rejected_names"],
        "elf_identity": manifest["elf_identity"],
    }


def operation_aliases(tiles: dict[str, Any], family: str) -> list[dict[str, Any]]:
    return [
        {
            "name": operation["name"],
            "classification": operation["classification"],
            "engine": operation["engine"],
            "function": operation["function"],
            "mnemonic": operation["command_mnemonic"],
            "semantic_status": operation["contract_status"],
            "semantic_handler": operation["semantic_handler"],
            "state_effects": operation["state_effects"],
        }
        for operation in tiles["operations"] if operation["family"] == family
    ]


def project_engine_ops(tiles: dict[str, Any]) -> dict[str, Any]:
    tepl_ops = []
    for operation in (item for item in tiles["operations"] if item["family"] == "TEPL"):
        entry = {
            key: operation[key] for key in (
                "name", "classification", "engine", "mode", "function",
                "semantic_handler", "legality_handler",
                "effect_contract", "fault_contract", "restart_contract", "operands", "state_effects"
            )
        }
        entry["profile"] = "v0.58"
        entry["logical_selector"] = int(operation["selector"], 16)
        entry["semantic_status"] = operation["contract_status"]
        tepl_ops.append(entry)
    current = {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/engine_ops.v0.json",
        "profile": "v0.58",
        "version": RELEASE,
        "source_lock": "isa/v0.58/pto-spec.lock.json",
        "note": (
            "PTO ISA 0.58 encoding families and semantic execution-engine annotations; "
            "TEPL remains an encoding carrier and is not a semantic engine."
        ),
        "semantic_engine_counts": dict(
            sorted(Counter(item["engine"] for item in tiles["operations"]).items())
        ),
    }
    current["tlsu"] = {
        "kind": "function_u5",
        "function_field_bits": [0, 4],
        "legal_aliases": operation_aliases(tiles, "TLSU"),
        "reserved_function_ranges": tiles["reserved"]["tlsu_functions"],
        "reserved_behavior": "illegal_instruction",
    }
    current["cube"] = {
        "kind": "function_u5",
        "function_field_bits": [0, 4],
        "legal_aliases": operation_aliases(tiles, "CUBE"),
        "unassigned_function_behavior": "illegal_instruction",
        "reserved_functions": tiles["reserved"]["cube_functions_without_named_alias"],
    }
    current["tepl"] = {
        "kind": "mode_function",
        "selector_formula": "(mode << 5) | function",
        "mode_field_bits": [0, 1],
        "function_field_bits": [0, 4],
        "accepted_selector_count": 86,
        "reserved_selector_ranges": tiles["reserved"]["tepl_selector_ranges"],
        "migration_aliases": {},
        "ops": tepl_ops,
    }
    current["tile_capacity_model"] = {
        "kind": "dynamic_per_descriptor",
        "cell_bytes": 128,
        "cells_per_pe": 2048,
        "capacity_bytes_per_pe": 262144,
        "b_iot_size_code_bytes": [
            None, 128, 256, 512, 1024, 2048, 4096, 8192,
            16384, 32768, 65536,
        ],
        "b_ios_size_code_bytes": [
            None, 128, 256, 512, 1024, 2048, 4096, 8192,
            16384, 32768, 65536, 131072, 262144,
        ],
        "normal_tile_min_bytes": 128,
        "normal_tile_max_bytes": 65536,
        "shape": {
            "rows": "SizeCodeBytes / (columns * element_size)",
            "rows_power_of_two": True,
            "columns_power_of_two": True,
            "valid_rows_at_most_rows": True,
            "valid_columns_at_most_columns": True,
            "matrix_operations_obey_same_shape_constraints": True,
        },
        "resource_shortage": "precise_allocation_trap",
        "eviction_or_spill": "forbidden",
        "physical_contiguity": "required",
    }
    current["shared_tile_registers"] = {
        "registers_per_core": 64,
        "assembly_names": "S0..S63",
        "addressing": "absolute-index",
        "sharing_domain": "one bank private to each core and shared by its four PEs",
        "quarter_selection": "B.IOS 3-bit PEMode decoded to the fixed four-PE mask; zero means NOP",
        "access": "all four PEs may access all shared registers and independently select tile offsets",
        "write_atomicity": "atomic descriptor-and-payload read-modify-write",
        "initial_state": "uninitialized; reads behave like undefined-register reads",
        "ordering": "no architectural order beyond atomicity; software prevents conflicting code/offset accesses",
        "allocation": "compiler-managed",
    }
    return current


def shared_register_state() -> dict[str, Any]:
    return {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/shared_tile_registers.v1.json",
        "profile": "v0.58",
        "version": RELEASE,
        "source_lock": "isa/v0.58/pto-spec.lock.json",
        "register_count": 64,
        "register_names": {"first": "S0", "last": "S63", "syntax": "S<absolute-index>"},
        "scope": {"private_to": "core", "shared_by": "four PEs in that core"},
        "semantics": {
            "atomicity": "descriptor-and-payload read-modify-write",
            "uninitialized_read": "undefined-register-value",
            "architectural_order": "none beyond atomicity",
            "conflict_avoidance": "programmer responsibility",
            "allocation": "compiler",
        },
        "pe_mode": {
            "owners": ["B.IOT", "B.IOS"],
            "width": 3,
            "kind": "fixed participation mode",
            "decoded_masks": ["0000", "1000", "0100", "0010", "0001", "1100", "1110", "1111"],
            "zero_behavior": "strict-no-effect-before-downstream-checks",
            "source_read_updates_descriptor": False,
            "destination_write_updates_descriptor": True,
        },
        "size_code_bytes": {
            "B.IOT": [None, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536],
            "B.IOS": [None, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144],
        },
        "gm_access": {
            "gpr_scope": "each selected PE resolves selectors in its private GPR file",
            "base_selector": "B.IOR.RegSrc0",
            "row_stride_selector": "B.IOR.RegSrc1",
            "row_stride_unit": "bytes",
            "omitted_b_ior": {
                "base": 0,
                "row_stride": "dense-row-bytes",
            },
            "explicit_zero_stride": "zero",
            "element_address": "base + row * row_stride_bytes + column * element_size",
            "packed_four_bit": "logical index selects containing byte and nibble",
            "preflight": "all selected accesses before effects",
            "pe_order": "none",
            "conflict_avoidance": "programmer responsibility",
            "b_iot_scope": "local-only",
        },
    }


def retired_encoding_state(tiles: dict[str, Any]) -> dict[str, Any]:
    return {
        "entries": [],
        "deleted_tile_names": tiles["deleted_names"],
        "migration_only_source_aliases": {},
        "notes": [
            "Deleted spellings and tile operations are assembler errors.",
            "Deleted scalar/block spellings do not retain encoding reservations in v0.58.",
            "Unassigned tile selectors remain illegal unless the PTO catalog assigns them.",
        ],
    }


def projections(docs: dict[str, dict[str, Any]]) -> dict[Path, dict[str, Any]]:
    state = PROFILE / "state"
    return {
        state / "pto_ops.json": project_pto_ops(docs["tiles"]),
        state / "pto_encoding_map.json": project_encoding_map(docs["tiles"]),
        state / "pto_command_forms.json": locked_projection(docs["commands"]),
        state / "pto_scalar_forms.json": locked_projection(docs["scalars"]),
        state / "extension_encoding_reservations.json": locked_projection(docs["reservations"]),
        state / "shared_tile_registers.json": shared_register_state(),
        state / "engine_ops.json": project_engine_ops(docs["tiles"]),
        PROFILE / "encoding/retired_encodings.json": retired_encoding_state(docs["tiles"]),
        PROFILE / "release_manifest.json": project_release_manifest(docs),
    }


def compare_or_write(expected: dict[Path, dict[str, Any]], check: bool) -> list[str]:
    errors = []
    for path, document in expected.items():
        rendered = pretty(document)
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != rendered:
                errors.append(f"out-of-date PTO projection: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--update-lock", action="store_true")
    args = parser.parse_args()
    try:
        docs = validate_source(args.source_root)
        upstream_lock = build_lock(args.source_root, docs)
        if args.update_lock:
            LOCK_PATH.write_text(pretty(upstream_lock), encoding="utf-8")
        elif load_json(LOCK_PATH) != upstream_lock:
            raise ValueError("checked-in pto-spec.lock.json does not match the upstream release")
        errors = compare_or_write(projections(docs), args.check)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"{'verified' if args.check else 'updated'} PTO ISA {RELEASE} lock and Linx projections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
