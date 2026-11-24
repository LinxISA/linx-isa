#!/usr/bin/env python3
"""Build truthful LinxISA v0.59.1 release-profile selection and packaging."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from build_linxisa_v0591_candidate import build as build_catalog
from build_linxisa_v0591_release_prep import build as build_release_prep


ROOT = Path(__file__).resolve().parents[2]
SELECTION = ROOT / "isa/profile-selection.json"
PACKAGE = ROOT / "isa/v0.59/release_package.json"
CATALOG = ROOT / "isa/v0.59/linxisa-v0.59.json"
LOCK = ROOT / "isa/v0.59/pto-spec.lock.json"
META = ROOT / "isa/v0.59/meta.json"
MANIFEST = ROOT / "isa/v0.59/release_manifest.json"

PACKAGE_INPUTS = (
    "isa/v0.59/linxisa-v0.59.json",
    "isa/v0.59/pto-v0591-candidate.json",
    "isa/v0.59/pto-spec.lock.json",
    "isa/v0.59/state/pto_tile_operations.json",
    "isa/v0.59/state/pto_system_registers.json",
    "isa/v0.59/state/pto_hardware_conformance_profile.json",
    "isa/v0.59/state/pto_hardware_numeric_vectors.json",
    "isa/v0.59/meta.json",
    "isa/v0.59/release_manifest.json",
    "isa/sail/model/linxisa_v0591_candidate.sail",
    "isa/sail/model/execute/v0591_candidate_dispatch.sail",
    "isa/sail/tests/v0591_candidate_dispatch_tests.sail",
    "isa/sail/toolchain.json",
    "tools/isa/build_linxisa_v0591_candidate.py",
    "tools/isa/build_pto_v0591_candidate.py",
    "tools/isa/build_linxisa_v0591_release_prep.py",
    "tools/isa/build_linxisa_v0591_release_activation.py",
    "tools/isa/build_golden.py",
    "tools/isa/export_linxisa_v0591_sail.py",
    "tools/isa/gen_sail_decode.py",
    "tools/isa/check_v0591_candidate_dispatch_sail.py",
    "tools/isa/select_linxisa_profile.py",
    "tools/isa/validate_spec.py",
)


def package_inputs() -> tuple[str, ...]:
    sail_sources = tuple(
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "isa/sail/model").rglob("*"))
        if path.is_file() and path.suffix in {".sail", ".sail_project"}
    )
    return tuple(dict.fromkeys((*PACKAGE_INPUTS, *sail_sources)))


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def render(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    catalog = build_catalog()
    if catalog != load(CATALOG):
        raise ValueError("v0.59 catalog differs from its deterministic builder")
    meta, manifest = build_release_prep()
    if meta != load(META) or manifest != load(MANIFEST):
        raise ValueError("v0.59 publication metadata or manifest is stale")
    if catalog.get("instruction_count") != 1499:
        raise ValueError("v0.59 release package requires all 1499 catalog rows")
    status = catalog.get("release_status", {})
    if status.get("state") != "published-specification-catalog":
        raise ValueError("v0.59 catalog is not the published specification catalog")
    if status.get("counts") != {"common": 578, "linx_only": 216, "scoped": 705}:
        raise ValueError("v0.59 catalog cardinality is not 578+216+705")
    lock = load(LOCK)
    toolchain = load(ROOT / "isa/sail/toolchain.json")

    selection = {
        "schema": "linxisa.profile-selection.v1",
        "default_profile": "v0.58",
        "policy": {
            "profile_must_be_explicit_for_prepublication": True,
            "prepublication_requires_opt_in": True,
            "published_nondefault_profiles_require_explicit_selection": True,
            "fallback_between_profiles_allowed": False,
        },
        "profiles": {
            "v0.58": {
                "state": "active-development-profile",
                "catalog": "isa/v0.58/linxisa-v0.58.json",
                "sail_entry": "isa/sail/model/linxisa.sail",
                "release_manifest": "isa/v0.58/release_manifest.json",
            },
            "v0.59": {
                "state": "published-explicit-profile",
                "version": "0.59.1",
                "catalog": "isa/v0.59/linxisa-v0.59.json",
                "sail_exporter": "tools/isa/export_linxisa_v0591_sail.py",
                "sail_entry": "model/linxisa_v0591.sail",
                "release_manifest": "isa/v0.59/release_manifest.json",
                "package": "isa/v0.59/release_package.json",
                "release_qualified": True,
                "qualification_scope": [
                    "architecture-specification",
                    "encoding",
                    "sail-package",
                ],
                "platform_qualified": False,
            },
        },
    }
    input_hashes = {
        relative: sha256(ROOT / relative) for relative in package_inputs()
    }
    package = {
        "schema": "linxisa.release-package.v1",
        "profile": "v0.59",
        "version": "0.59.1",
        "state": "published-specification",
        "publication_allowed": True,
        "default_profile": "v0.58",
        "profile_selection": {
            "path": "isa/profile-selection.json",
            "sha256": canonical_sha256(selection),
        },
        "identity": manifest["identity"],
        "catalog": {
            **manifest["catalog"],
            "instruction_count": catalog["instruction_count"],
            "counts": status["counts"],
        },
        "sail": {
            "entry": "model/linxisa_v0591.sail",
            "exporter": "tools/isa/export_linxisa_v0591_sail.py",
            "source_entry": "isa/sail/model/linxisa_v0591_candidate.sail",
            "dispatch": "isa/sail/model/execute/v0591_candidate_dispatch.sail",
            "directed_tests": "isa/sail/tests/v0591_candidate_dispatch_tests.sail",
            "toolchain": toolchain,
            "state": "published-catalog-and-scoped-dispatch",
        },
        "inputs": input_hashes,
        "inputs_sha256": canonical_sha256(input_hashes),
        "upstream_source_hashes": {
            "tile_operations": lock["catalogs"]["tile_operations"],
            "system_registers": lock["catalogs"]["system_registers"],
            "hardware_conformance_profile": lock["hardware_conformance_profile"],
            "numeric_conformance_vectors": lock["numeric_conformance_vectors"],
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
            "component_pins_qualified": False,
            "linux_qualified": False,
            "system_runtime_qualified": False,
            "platform_qualified": False,
            "evidence": {
                "catalog_builder": "tools/isa/build_linxisa_v0591_candidate.py --check",
                "encoding_validator": "tools/isa/validate_spec.py --profile v0.59",
                "sail_validator": "tools/isa/check_v0591_candidate_dispatch_sail.py",
            },
            "remaining": list(
                manifest["qualification"]["remaining_platform_qualification"]
            ),
        },
        "activation_policy": {
            "explicit_profile_ready": True,
            "published_default_switch_requires_platform_qualification": True,
            "default_switch_requested": False,
        },
        "required_checks": [
            "python3 tools/isa/build_golden.py --profile v0.59 --check",
            "python3 tools/isa/validate_spec.py --profile v0.59",
            "python3 tools/isa/check_v0591_candidate_dispatch_sail.py",
            "python3 tools/isa/build_linxisa_v0591_release_activation.py --check",
        ],
    }
    return selection, package


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    from check_linxisa_v0591_release_compat import check as check_compatibility

    compatibility_errors = check_compatibility()
    if compatibility_errors:
        raise SystemExit(
            "v0.59.1 release compatibility failed: "
            + "; ".join(compatibility_errors)
        )
    if args.check:
        print("LinxISA v0.59.1 immutable release and registry slice are current")
        return 0

    current_selection = load(SELECTION)
    frozen_selection, _package = build()
    extra_profiles = set(current_selection.get("profiles", {})) - set(
        frozen_selection["profiles"]
    )
    if extra_profiles:
        print(
            "preserved immutable v0.59.1 package and extended profile registry; "
            f"newer profiles: {', '.join(sorted(extra_profiles))}"
        )
        return 0

    try:
        selection, package = build()
    except (KeyError, OSError, ValueError) as error:
        raise SystemExit(f"v0.59.1 release activation failed: {error}") from error
    outputs = ((SELECTION, render(selection)), (PACKAGE, render(package)))
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
