#!/usr/bin/env python3
"""Build inactive LinxISA v0.59.1 profile metadata and release preparation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from build_linxisa_v0591_candidate import build as build_catalog


ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "isa/v0.59"
CATALOG = PROFILE / "linxisa-v0.59.json"
BINDINGS = PROFILE / "pto-v0591-candidate.json"
LOCK = PROFILE / "pto-spec.lock.json"
META = PROFILE / "meta.json"
MANIFEST = PROFILE / "release_manifest.json"
V058_MANIFEST = ROOT / "isa/v0.58/release_manifest.json"


def load(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return document


def render(document: object) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    catalog = build_catalog()
    if catalog != load(CATALOG):
        raise ValueError("canonical v0.59.1 prepublication catalog is stale")
    lock = load(LOCK)
    bindings = load(BINDINGS)
    counts = catalog["candidate_status"]["counts"]
    expected_counts = {"common": 578, "linx_only": 216, "scoped": 705}
    if counts != expected_counts or catalog["instruction_count"] != 1499:
        raise ValueError("v0.59.1 catalog cardinality differs from 578+216+705")
    binding_sha = sha256(BINDINGS)
    if binding_sha != catalog["candidate_status"]["source_bindings_sha256"]:
        raise ValueError("catalog source binding hash differs from the frozen file")

    identity = {
        key: lock[key]
        for key in ("encoding_abi", "encoding_projection_sha256", "release")
    }
    meta = {
        "isa": "LinxISA",
        "version": "0.59.1",
        "status": "inactive-prepublication",
        "instruction_lengths_bits": [16, 32, 48, 64],
        "cardinality": {
            "instructions": 1499,
            "common_forms": counts["common"],
            "linx_only_forms": counts["linx_only"],
            "scoped_forms": counts["scoped"],
        },
        "catalog": "isa/v0.59/linxisa-v0.59.json",
        "release_activation": {
            "state": "prepared-prepublication",
            "profile_selection": "isa/profile-selection.json",
            "package": "isa/v0.59/release_package.json",
            "sail_entry": "isa/sail/model/linxisa_v0591_candidate.sail",
            "default_profile_changed": False,
        },
        "notes": [
            "This is a reproducible prepublication profile; v0.58 remains the default and active profile.",
            "The 578 common and 705 scoped forms come from the exact frozen PTO ISA 0.59.1 lock; 216 Linx-only rows are preserved from v0.58.",
            "Catalog presence does not claim Linux, component-leaf, system-runtime, or release qualification.",
        ],
    }
    manifest = {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/release_manifest.v1.json",
        "profile": "v0.59",
        "version": "0.59.1",
        "source_lock": "isa/v0.59/pto-spec.lock.json",
        "policy": {
            "pto_spec_is_sole_source_for_common_and_scoped_forms": True,
            "linx_only_rows_are_preserved_from_v0.58": True,
            "legacy_decode_allowed": False,
            "default_profile_changed": False,
        },
        "cardinality": {
            "instructions": 1499,
            "common_forms": counts["common"],
            "linx_only_forms": counts["linx_only"],
            "scoped_forms": counts["scoped"],
            "scalar_forms": int(lock["catalogs"]["scalar_forms"]["count"]),
            "command_forms": int(lock["catalogs"]["command_forms"]["count"]),
            "tile_operations": int(lock["catalogs"]["tile_operations"]["count"]),
            "system_registers": int(lock["catalogs"]["system_registers"]["count"]),
            "extension_encoding_reservations": int(
                lock["catalogs"]["extension_encoding_reservations"]["count"]
            ),
        },
        "catalog": {
            "path": "isa/v0.59/linxisa-v0.59.json",
            "sha256": sha256(CATALOG),
            "schema": catalog["schema"],
            "status": catalog["candidate_status"]["state"],
        },
        "frozen_bindings": {
            "path": "isa/v0.59/pto-v0591-candidate.json",
            "sha256": binding_sha,
            "schema": bindings["schema"],
        },
        "elf_identity": load(V058_MANIFEST)["elf_identity"],
        "status": "development-not-published",
        "identity": identity,
        "publication": None,
        "release_activation": {
            "state": "prepared-prepublication",
            "profile_selection": "isa/profile-selection.json",
            "package": "isa/v0.59/release_package.json",
            "catalog": "isa/v0.59/linxisa-v0.59.json",
            "sail_entry": "isa/sail/model/linxisa_v0591_candidate.sail",
            "default_profile": "v0.58",
        },
        "qualification": {
            "release_qualified": False,
            "linux_qualified": False,
            "leaf_components_qualified": False,
            "system_runtime_qualified": False,
            "required_before_publication": [
                "activate the packaged scoped Sail entry as the published v0.59 entry after exact release gates pass",
                "promote exact reviewed component pins in the owning superproject change",
                "complete Linux and leaf-component validation at those exact pins",
                "run release verification and release preparation on the final main commit",
                "record publication metadata and create the release tag only after all gates pass",
            ],
        },
    }
    return meta, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        meta, manifest = build()
    except (KeyError, OSError, ValueError) as error:
        raise SystemExit(
            f"LinxISA v0.59.1 release preparation failed: {error}"
        ) from error
    outputs = ((META, render(meta)), (MANIFEST, render(manifest)))
    if args.check:
        stale = [
            path
            for path, expected in outputs
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]
        if stale:
            raise SystemExit(f"stale LinxISA v0.59.1 release preparation: {stale}")
        print("LinxISA v0.59.1 prepublication metadata and manifest are current")
        return 0
    for path, content in outputs:
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
