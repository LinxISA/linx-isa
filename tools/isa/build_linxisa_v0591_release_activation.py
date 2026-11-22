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
    "isa/v0.59/meta.json",
    "isa/v0.59/release_manifest.json",
    "isa/sail/model/linxisa_v0591_candidate.sail",
    "isa/sail/model/execute/v0591_candidate_dispatch.sail",
    "isa/sail/tests/v0591_candidate_dispatch_tests.sail",
    "isa/sail/toolchain.json",
    "tools/isa/build_linxisa_v0591_candidate.py",
    "tools/isa/build_linxisa_v0591_release_prep.py",
    "tools/isa/build_linxisa_v0591_release_activation.py",
    "tools/isa/build_golden.py",
    "tools/isa/export_linxisa_v0591_sail.py",
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
        raise ValueError("v0.59 prepublication metadata or manifest is stale")
    if catalog.get("instruction_count") != 1499:
        raise ValueError("v0.59 release package requires all 1499 catalog rows")
    status = catalog.get("candidate_status", {})
    if status.get("state") != "prepublication-full-catalog":
        raise ValueError("v0.59 catalog must remain explicitly prepublication")
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
                "state": "selectable-prepublication",
                "version": "0.59.1",
                "catalog": "isa/v0.59/linxisa-v0.59.json",
                "sail_exporter": "tools/isa/export_linxisa_v0591_sail.py",
                "sail_entry": "model/linxisa_v0591.sail",
                "release_manifest": "isa/v0.59/release_manifest.json",
                "package": "isa/v0.59/release_package.json",
                "release_qualified": False,
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
        "state": "prepared-prepublication",
        "publication_allowed": False,
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
            "state": "assembled-catalog-and-scoped-dispatch-prepared",
        },
        "inputs": input_hashes,
        "inputs_sha256": canonical_sha256(input_hashes),
        "qualification": {
            "release_qualified": False,
            "component_pins_qualified": False,
            "linux_qualified": False,
            "system_runtime_qualified": False,
            "evidence": None,
            "remaining": list(
                manifest["qualification"]["required_before_publication"]
            ),
        },
        "activation_policy": {
            "explicit_profile_ready": True,
            "published_default_switch_requires_release_qualification": True,
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
    try:
        selection, package = build()
    except (KeyError, OSError, ValueError) as error:
        raise SystemExit(f"v0.59.1 release activation failed: {error}") from error
    outputs = ((SELECTION, render(selection)), (PACKAGE, render(package)))
    if args.check:
        stale = [
            path
            for path, expected in outputs
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]
        if stale:
            raise SystemExit(f"stale v0.59.1 release activation: {stale}")
        print("LinxISA v0.59.1 release activation package is current")
        return 0
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
