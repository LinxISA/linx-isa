#!/usr/bin/env python3
"""Build LinxISA 0.59.2 release metadata for the obsolescence decision."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from build_linxisa_v0592_catalog import build as build_catalog


ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "isa/v0.59.2"
CATALOG = PROFILE / "linxisa-v0.59.2.json"
META = PROFILE / "meta.json"
MANIFEST = PROFILE / "release_manifest.json"
SOURCE_LOCK = ROOT / "isa/v0.59/pto-spec.lock.json"
RESERVATIONS = ROOT / "isa/v0.59/state/extension_encoding_reservations.json"
DECISION = ROOT / "docs/architecture/linx-two-level-block-obsolescence.md"
V0591_MANIFEST = ROOT / "isa/v0.59/release_manifest.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    catalog = build_catalog()
    if catalog != load(CATALOG):
        raise ValueError("canonical 0.59.2 catalog is stale")
    lock = load(SOURCE_LOCK)
    prior_manifest = load(V0591_MANIFEST)
    counts = catalog["release_status"]["linx_only_status_counts"]
    source_identity = {
        key: lock[key]
        for key in ("encoding_abi", "encoding_projection_sha256", "release")
    }
    inherited_sources = prior_manifest["authoritative_sources"]
    for source in inherited_sources.values():
        path = ROOT / source["path"]
        if not path.is_file() or sha256(path) != source["sha256"]:
            raise ValueError(f"inherited authoritative source hash differs: {path}")
    sources = {
        **inherited_sources,
        "catalog": {
            "path": "isa/v0.59.2/linxisa-v0.59.2.json",
            "sha256": sha256(CATALOG),
        },
        "pto_lock": {
            "path": "isa/v0.59/pto-spec.lock.json",
            "sha256": sha256(SOURCE_LOCK),
        },
        "pto_reservations": {
            "path": "isa/v0.59/state/extension_encoding_reservations.json",
            "sha256": sha256(RESERVATIONS),
            "count": 50,
        },
        "architecture_decision": {
            "path": "docs/architecture/linx-two-level-block-obsolescence.md",
            "sha256": sha256(DECISION),
        },
    }
    meta = {
        "isa": "LinxISA",
        "version": "0.59.2",
        "status": "published-specification",
        "instruction_lengths_bits": [16, 32, 48, 64],
        "cardinality": {
            "instructions": 1499,
            "common_forms": 578,
            "linx_only_forms": 216,
            "scoped_forms": 705,
            **{f"linx_only_{key}_forms": value for key, value in counts.items()},
        },
        "authoritative_sources": sources,
        "catalog": "isa/v0.59.2/linxisa-v0.59.2.json",
    }
    manifest = {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/release_manifest.v1.json",
        "profile": "v0.59.2",
        "version": "0.59.2",
        "source_lock": "isa/v0.59/pto-spec.lock.json",
        "upstream_pto": {
            "release": lock["release"],
            "specification_status": lock["specification_status"],
            "publication": lock["publication"],
        },
        "policy": {
            "pto_spec_is_sole_source_for_common_and_scoped_forms": True,
            "common_scoped_encoding_and_semantics_unchanged_from": "0.59.1",
            "obsolete_encodings_remain_reserved": True,
            "obsolete_form_execution": "v0.59.1-compatible-in-published-sail",
            "default_profile_changed": False,
        },
        "cardinality": meta["cardinality"],
        "authoritative_sources": sources,
        "catalog": {
            **sources["catalog"],
            "schema": catalog["schema"],
            "status": catalog["release_status"]["state"],
        },
        "status": "published-specification",
        "identity": source_identity,
        "elf_identity": prior_manifest["elf_identity"],
        "publication": {
            "version": "0.59.2",
            "date": "2026-11-24",
            "scope": ["architecture-specification", "encoding", "sail-package"],
            "profile_selection": "explicit-v0.59.2",
        },
        "release_activation": {
            "state": "published-explicit-profile",
            "profile_selection": "isa/profile-selection.json",
            "package": "isa/v0.59.2/release_package.json",
            "catalog": "isa/v0.59.2/linxisa-v0.59.2.json",
            "sail_exporter": "tools/isa/export_linxisa_v0592_sail.py",
            "sail_entry": "model/linxisa_v0592.sail",
            "default_profile": "v0.58",
        },
        "qualification": {
            "release_qualified": True,
            "qualification_scope": [
                "architecture-specification",
                "encoding",
                "sail-package",
            ],
            "specification_qualified": True,
            "encoding_qualified": True,
            "sail_package_qualified": True,
            "linux_qualified": False,
            "leaf_components_qualified": False,
            "system_runtime_qualified": False,
            "platform_qualified": False,
            "remaining_platform_qualification": [
                "qualify downstream assembler, disassembler and emulator obsolete-form policy",
                "qualify RTL against the published obsolete-form and encoding-reservation status",
                "qualify Linux, leaf components and full system runtime at exact reviewed pins",
                "switch the default platform profile only after exact platform gates pass",
            ],
        },
    }
    return meta, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    meta, manifest = build()
    outputs = ((META, render(meta)), (MANIFEST, render(manifest)))
    if args.check:
        stale = [
            str(path)
            for path, text in outputs
            if not path.is_file() or path.read_text(encoding="utf-8") != text
        ]
        if stale:
            raise SystemExit("stale 0.59.2 release metadata: " + ", ".join(stale))
        print("LinxISA 0.59.2 release metadata is current")
        return 0
    PROFILE.mkdir(parents=True, exist_ok=True)
    for path, text in outputs:
        path.write_text(text, encoding="utf-8")
    print(f"wrote {META} and {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
