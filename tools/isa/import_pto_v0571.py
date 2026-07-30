#!/usr/bin/env python3
"""Import the canonical PTO ISA 0.57.1 release into the Linx v0.57 profile.

The lock file is the only checked-in location that repeats the upstream commit
and release hashes.  The three state files produced here are deterministic
projections of the locked upstream catalogs; they name the lock instead of
copying its identity fields.
"""

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
PROFILE = ROOT / "isa" / "v0.57"
LOCK_PATH = PROFILE / "pto-spec.lock.json"
RELEASE = "0.57.1"
EXPECTED_ABI = "pto-isa-0.57.1-mode-function-v1"


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


def source_paths(source_root: Path) -> tuple[Path, Path, Path, Path, Path]:
    return (
        source_root / "spec" / "release-manifest.json",
        source_root / "spec" / "catalog" / "tile-operations.json",
        source_root / "spec" / "catalog" / "command-forms.json",
        source_root / "spec" / "hardware-conformance-profile.json",
        source_root / "spec" / "evidence" / "pto-isa-0571-hardware-numeric-vectors.json",
    )


def validate_source(source_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest_path, tile_path, command_path, hardware_path, vectors_path = source_paths(source_root)
    for path in (manifest_path, tile_path, command_path, hardware_path, vectors_path):
        if not path.is_file():
            raise ValueError(f"missing upstream PTO source: {path}")

    manifest = load_json(manifest_path)
    tiles = load_json(tile_path)
    commands = load_json(command_path)
    hardware = load_json(hardware_path)
    vectors = load_json(vectors_path)
    if manifest.get("release") != RELEASE:
        raise ValueError(f"upstream release must be {RELEASE}")
    if manifest.get("encoding_abi") != EXPECTED_ABI:
        raise ValueError(f"unexpected encoding ABI: {manifest.get('encoding_abi')!r}")
    counts = manifest.get("catalog_counts") or {}
    if counts.get("tile_operations_total") != 120 or counts.get("command_forms") != 99:
        raise ValueError("upstream manifest must publish 120 tile operations and 99 command forms")
    if tiles.get("operation_count") != 120 or len(tiles.get("operations") or []) != 120:
        raise ValueError("upstream tile catalog is not the exact 120-operation release")
    if commands.get("form_count") != 99 or len(commands.get("forms") or []) != 99:
        raise ValueError("upstream command catalog is not the exact 99-form release")

    canonical = {entry["path"]: entry["sha256"] for entry in manifest["canonical_inputs"]}
    for path, rel in ((tile_path, "spec/catalog/tile-operations.json"),
                      (command_path, "spec/catalog/command-forms.json")):
        actual = sha256(path)
        if canonical.get(rel) != actual:
            raise ValueError(f"{rel} does not match the release manifest: {actual}")

    hardware_manifest = manifest.get("hardware_conformance_profile") or {}
    if hardware_manifest.get("path") != "spec/hardware-conformance-profile.json":
        raise ValueError("release manifest names the wrong hardware conformance profile")
    if hardware_manifest.get("evidence") != "spec/evidence/pto-isa-0571-hardware-numeric-vectors.json":
        raise ValueError("release manifest names the wrong hardware numeric evidence")
    if hardware_manifest.get("sha256") != sha256(hardware_path):
        raise ValueError("hardware conformance profile does not match the release manifest")
    if hardware.get("profile_id") != hardware_manifest.get("profile_id"):
        raise ValueError("hardware profile identity differs from the release manifest")
    if vectors.get("hardware_profile_id") != hardware.get("profile_id"):
        raise ValueError("numeric vectors target a different hardware profile")
    if vectors.get("hardware_profile_sha256") != sha256(hardware_path):
        raise ValueError("numeric vectors target a different hardware profile hash")
    return manifest, tiles, commands


def build_lock(source_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    manifest_path, tile_path, command_path, hardware_path, vectors_path = source_paths(source_root)
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=source_root, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"cannot resolve upstream git commit: {exc}") from exc
    return {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/pto_spec_lock.v1.json",
        "catalogs": {
            "command_forms": {
                "path": "spec/catalog/command-forms.json",
                "sha256": sha256(command_path),
                "count": 99,
            },
            "tile_operations": {
                "path": "spec/catalog/tile-operations.json",
                "sha256": sha256(tile_path),
                "count": 120,
            },
        },
        "content_sha256": manifest["content_sha256"],
        "encoding_abi": manifest["encoding_abi"],
        "encoding_projection_sha256": manifest["encoding_projection_sha256"],
        "hardware_conformance_profile": {
            "path": "spec/hardware-conformance-profile.json",
            "profile_id": manifest["hardware_conformance_profile"]["profile_id"],
            "sha256": sha256(hardware_path),
        },
        "numeric_conformance_vectors": {
            "path": "spec/evidence/pto-isa-0571-hardware-numeric-vectors.json",
            "sha256": sha256(vectors_path),
        },
        "release": manifest["release"],
        "release_manifest": {
            "path": "spec/release-manifest.json",
            "sha256": sha256(manifest_path),
        },
        "source": {
            "commit": commit,
            "repository": "https://github.com/PTO-ISA/pto-spec.git",
        },
    }


def project_pto_ops(tiles: dict[str, Any]) -> dict[str, Any]:
    counts = Counter(operation["family"] for operation in tiles["operations"])
    return {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/pto_ops.v1.json",
        "profile": "v0.57",
        "version": RELEASE,
        "source_lock": "isa/v0.57/pto-spec.lock.json",
        "operation_count": len(tiles["operations"]),
        "family_counts": dict(sorted(counts.items())),
        "deleted_names": tiles["deleted_names"],
        "rejected_names": tiles["rejected_names"],
        "reserved": tiles["reserved"],
        "operations": tiles["operations"],
    }


def project_encoding_map(tiles: dict[str, Any]) -> dict[str, Any]:
    entries = []
    for operation in tiles["operations"]:
        entries.append({
            "name": operation["name"],
            "family": operation["family"],
            "command_mnemonic": operation["command_mnemonic"],
            "selector": operation.get("selector"),
            "mode": operation.get("mode"),
            "function": operation.get("function"),
            "disposition": operation["disposition"],
            "contract_status": operation["contract_status"],
        })
    counts = Counter(entry["family"] for entry in entries)
    return {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/pto_encoding_map.v1.json",
        "profile": "v0.57",
        "version": RELEASE,
        "source_lock": "isa/v0.57/pto-spec.lock.json",
        "policy": {
            "catalog_order_allocates_encodings": False,
            "unlisted_selectors_reserved": True,
            "legacy_decode_allowed": False,
            "source_aliases_are_migration_only": True,
        },
        "entry_count": len(entries),
        "family_counts": dict(sorted(counts.items())),
        "migration_aliases": {"TTRANSPOSE": "TTRANS", "TSORT32": "TSORT"},
        "entries": entries,
    }


def project_command_forms(commands: dict[str, Any]) -> dict[str, Any]:
    result = dict(commands)
    result["source_lock"] = "isa/v0.57/pto-spec.lock.json"
    return result


def project_release_manifest(
    manifest: dict[str, Any], tiles: dict[str, Any], commands: dict[str, Any]
) -> dict[str, Any]:
    return {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/release_manifest.v1.json",
        "profile": "v0.57",
        "version": RELEASE,
        "source_lock": "isa/v0.57/pto-spec.lock.json",
        "policy": {
            "pto_spec_is_sole_source": True,
            "legacy_decode_allowed": False,
            "unlisted_selectors_reserved": True,
            "migration_aliases_are_source_only": True,
        },
        "cardinality": {
            "tile_operations": len(tiles["operations"]),
            "tile_families": dict(Counter(item["family"] for item in tiles["operations"])),
            "command_forms": len(commands["forms"]),
            "command_form_families": manifest["catalog_counts"]["command_form_families"],
            "scalar_forms": manifest["catalog_counts"]["scalar_forms"],
        },
        "migration_aliases": {"TTRANSPOSE": "TTRANS", "TSORT32": "TSORT"},
        "deleted_names": tiles["deleted_names"],
        "rejected_names": tiles["rejected_names"],
        "elf_identity": manifest["elf_identity"],
    }


def project_engine_ops(tiles: dict[str, Any]) -> dict[str, Any]:
    current = load_json(PROFILE / "state" / "engine_ops.json")
    old_tepl = {entry["name"]: entry for entry in current["tepl"]["ops"]}
    if "TTRANSPOSE" in old_tepl and "TTRANS" not in old_tepl:
        old_tepl["TTRANS"] = old_tepl["TTRANSPOSE"]

    tepl_ops = []
    for operation in (item for item in tiles["operations"] if item["family"] == "TEPL"):
        entry = dict(old_tepl.get(operation["name"], {}))
        entry.pop("tile_opcode", None)
        entry.update({
            "name": operation["name"],
            "mode": operation["mode"],
            "function": operation["function"],
            "logical_selector": int(operation["selector"], 16),
            "semantic_status": operation["contract_status"],
            "semantic_handler": operation["semantic_handler"],
            "legality_handler": operation["legality_handler"],
            "effect_contract": operation["effect_contract"],
            "fault_contract": operation["fault_contract"],
            "restart_contract": operation["restart_contract"],
            "operands": operation["operands"],
            "state_effects": operation["state_effects"],
        })
        tepl_ops.append(entry)

    def aliases(family: str) -> list[dict[str, Any]]:
        result = []
        for operation in tiles["operations"]:
            if operation["family"] != family:
                continue
            result.append({
                "name": operation["name"],
                "function": operation["function"],
                "mnemonic": operation["command_mnemonic"],
                "semantic_status": operation["contract_status"],
                "semantic_handler": operation["semantic_handler"],
                "state_effects": operation["state_effects"],
            })
        return result

    current.update({
        "profile": "v0.57",
        "version": RELEASE,
        "source_lock": "isa/v0.57/pto-spec.lock.json",
        "note": "Linx scheduling metadata projected onto the normative PTO ISA 0.57.1 tile catalog.",
    })
    current["tma"] = {
        "kind": "function_u5",
        "function_field_bits": [0, 4],
        "legal_aliases": aliases("TMA"),
        "reserved_function_range": [9, 31],
        "reserved_behavior": "illegal_instruction",
    }
    current["cube"] = {
        "kind": "function_u5",
        "function_field_bits": [0, 4],
        "legal_aliases": aliases("CUBE"),
        "unassigned_function_behavior": "illegal_instruction",
        "reserved_functions": tiles["reserved"]["cube_functions_without_named_alias"],
    }
    current["tepl"] = {
        "kind": "mode_function",
        "selector_formula": "(mode << 5) | function",
        "mode_field_bits": [0, 1],
        "function_field_bits": [0, 4],
        "accepted_selector_count": 98,
        "reserved_selector_ranges": tiles["reserved"]["tepl_selector_ranges"],
        "migration_aliases": {"TTRANSPOSE": "TTRANS", "TSORT32": "TSORT"},
        "ops": tepl_ops,
    }
    current["tile_capacity_model"] = {
        "kind": "dynamic_per_descriptor",
        "cell_bytes": 128,
        "cells_per_pe": 2048,
        "capacity_bytes_per_pe": 262144,
        "b_iot_size_imm4_bytes": [None, None, None, 128, 256, 512, 1024, 2048, 4096, 8192,
                                      None, None, None, None, None, None],
        "normal_tile_min_bytes": 128,
        "normal_tile_max_bytes": 8192,
        "resource_shortage": "precise_allocation_trap",
        "eviction_or_spill": "forbidden",
        "physical_contiguity": "required",
    }
    return current


def projections(
    manifest: dict[str, Any], tiles: dict[str, Any], commands: dict[str, Any]
) -> dict[Path, dict[str, Any]]:
    state = PROFILE / "state"
    return {
        state / "pto_ops.json": project_pto_ops(tiles),
        state / "pto_encoding_map.json": project_encoding_map(tiles),
        state / "pto_command_forms.json": project_command_forms(commands),
        state / "engine_ops.json": project_engine_ops(tiles),
        PROFILE / "release_manifest.json": project_release_manifest(manifest, tiles, commands),
    }


def compare_or_write(expected: dict[Path, dict[str, Any]], check: bool) -> list[str]:
    errors = []
    for path, document in expected.items():
        rendered = pretty(document)
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != rendered:
                errors.append(f"out-of-date PTO projection: {path.relative_to(ROOT)}")
        else:
            path.write_text(rendered, encoding="utf-8")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--update-lock", action="store_true")
    args = parser.parse_args()
    try:
        manifest, tiles, commands = validate_source(args.source_root)
        upstream_lock = build_lock(args.source_root, manifest)
        if args.update_lock:
            LOCK_PATH.write_text(pretty(upstream_lock), encoding="utf-8")
        elif load_json(LOCK_PATH) != upstream_lock:
            raise ValueError("checked-in pto-spec.lock.json does not match the upstream release")
        errors = compare_or_write(projections(manifest, tiles, commands), args.check)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    action = "verified" if args.check else "updated"
    print(f"{action} PTO ISA {RELEASE} lock and Linx projections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
