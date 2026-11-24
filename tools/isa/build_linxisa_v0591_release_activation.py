#!/usr/bin/env python3
"""Build truthful LinxISA v0.59.1 release-profile selection and packaging."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

from build_linxisa_v0591_candidate import PUBLICATION_REVISION
from build_linxisa_v0591_candidate import REMOVED_BLOCK_MNEMONICS
from build_linxisa_v0591_candidate import SIGNED_BASELINE
from build_linxisa_v0591_candidate import build as build_catalog
from build_linxisa_v0591_release_prep import build as build_release_prep
from export_linxisa_v0591_sail import export as export_sail, package_sources


ROOT = Path(__file__).resolve().parents[2]
SELECTION = ROOT / "isa/profile-selection.json"
PACKAGE = ROOT / "isa/v0.59/release_package.json"
CATALOG = ROOT / "isa/v0.59/linxisa-v0.59.json"
LOCK = ROOT / "isa/v0.59/pto-spec.lock.json"
META = ROOT / "isa/v0.59/meta.json"
MANIFEST = ROOT / "isa/v0.59/release_manifest.json"
RESERVATIONS = ROOT / "isa/v0.59/state/extension_encoding_reservations.json"

PACKAGE_INPUTS = (
    "isa/v0.59/linxisa-v0.59.json",
    "isa/v0.59/pto-v0591-candidate.json",
    "isa/v0.59/pto-spec.lock.json",
    "isa/v0.59/meta.json",
    "isa/v0.59/release_manifest.json",
    "isa/v0.59/sail/v0591_hard_break_tests.sail",
    "isa/v0.59/sail/README.md",
    "isa/sail/model/execute/v0591_candidate_dispatch.sail",
    "isa/sail/toolchain.json",
    "tools/isa/build_linxisa_v0591_candidate.py",
    "tools/isa/build_pto_v0591_candidate.py",
    "tools/isa/build_linxisa_v0591_release_prep.py",
    "tools/isa/build_linxisa_v0591_release_activation.py",
    "tools/isa/build_golden.py",
    "tools/isa/export_linxisa_v0591_sail.py",
    "tools/isa/gen_sail_decode.py",
    "tools/isa/check_v0591_candidate_dispatch_sail.py",
    "tools/isa/test_v0591_sail_hard_break.py",
    "tools/isa/v0591_sail_hard_break.py",
    "tools/isa/select_linxisa_profile.py",
    "tools/isa/validate_spec.py",
)


def package_inputs() -> tuple[str, ...]:
    state_sources = tuple(
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "isa/v0.59/state").glob("*.json"))
    )
    sail_sources = tuple(
        path.relative_to(ROOT).as_posix() for path in sorted(package_sources().values())
    )
    return tuple(dict.fromkeys((*PACKAGE_INPUTS, *state_sources, *sail_sources)))


def hard_reject_reservations() -> list[dict[str, Any]]:
    names = {"V.*", *REMOVED_BLOCK_MNEMONICS}
    rows = [
        row
        for row in load(RESERVATIONS)["reservations"]
        if row.get("mnemonic") in names
    ]
    if len(rows) != 10 or {row["mnemonic"] for row in rows} != names:
        raise ValueError("the ten removed execution encoding ranges are not reserved")
    if any(row.get("status") != "reserved-in-pto" for row in rows):
        raise ValueError("a removed execution encoding range is not reserved in PTO")
    return rows


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
    if catalog.get("instruction_count") != 1306:
        raise ValueError("v0.59 release package requires exactly 1306 catalog rows")
    status = catalog.get("release_status", {})
    if status.get("state") != "local-release-ready":
        raise ValueError("v0.59 catalog is not locally release-ready")
    if status.get("counts") != {"common": 578, "linx_only": 23, "scoped": 705}:
        raise ValueError("v0.59 catalog cardinality is not 578+23+705")
    lock = load(LOCK)
    toolchain = load(ROOT / "isa/sail/toolchain.json")
    hard_reject = hard_reject_reservations()
    with tempfile.TemporaryDirectory(prefix="linx-v0591-release-sail-") as directory:
        sail_package = export_sail(Path(directory) / "sail")

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
                "state": "release-ready-explicit-profile",
                "version": "0.59.1",
                "publication_revision": PUBLICATION_REVISION,
                "catalog": "isa/v0.59/linxisa-v0.59.json",
                "sail_exporter": "tools/isa/export_linxisa_v0591_sail.py",
                "sail_entry": "model/linxisa_v0591.sail",
                "release_manifest": "isa/v0.59/release_manifest.json",
                "package": "isa/v0.59/release_package.json",
                "release_qualified": True,
                "qualification_scope": [
                    "source",
                    "architecture-specification",
                    "encoding",
                    "sail-package",
                ],
                "platform_qualified": False,
            },
        },
    }
    input_hashes = {relative: sha256(ROOT / relative) for relative in package_inputs()}
    package = {
        "schema": "linxisa.release-package.v1",
        "profile": "v0.59",
        "version": "0.59.1",
        "publication_revision": PUBLICATION_REVISION,
        "signed_baseline": SIGNED_BASELINE,
        "state": "local-release-ready",
        "publication_allowed": True,
        "external_publication_record": {
            "kind": "github-release-url",
            "tracking": "external",
            "embedded_value": None,
        },
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
            "source_entry": "isa/v0.59/sail/model/linxisa_v0591.sail",
            "dispatch": "isa/sail/model/execute/v0591_candidate_dispatch.sail",
            "directed_tests": "isa/v0.59/sail/v0591_candidate_dispatch_tests.sail",
            "release_readme": "isa/v0.59/sail/README.md",
            "toolchain": toolchain,
            "state": "qualified-hard-break-package",
            "files_sha256": sail_package["files_sha256"],
            "hard_break": sail_package["hard_break"],
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
                "source",
                "architecture-specification",
                "encoding",
                "sail-package",
            ],
            "source_qualified": True,
            "specification_qualified": True,
            "encoding_qualified": True,
            "sail_package_qualified": True,
            "compiler_qualified": False,
            "component_pins_qualified": False,
            "rtl_qualified": False,
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
            "release_ready": True,
            "published_default_switch_requires_platform_qualification": True,
            "default_switch_requested": False,
        },
        "hard_reject_reserved_encodings": {
            "count": 10,
            "decode_policy": "hard-reject-before-operand-read-or-architectural-effect",
            "reallocation_allowed": False,
            "ranges": hard_reject,
        },
        "approval_gates": {
            "state": "release-ready",
            "validated_scope_approved": True,
            "sail_input_hashes_locked": True,
            "html_validation_passed": True,
            "release_action_permitted": True,
            "operator_publication_required": True,
        },
        "required_checks": [
            "python3 tools/isa/build_golden.py --profile v0.59 --check",
            "python3 tools/isa/validate_spec.py --profile v0.59",
            "opam exec -- python3 tools/isa/check_v0591_candidate_dispatch_sail.py",
            "python3 -m unittest tools.isa.test_v0591_sail_hard_break",
            "python3 tools/isa/export_linxisa_v0591_sail.py --check <release-sail-directory>",
            "make -C docs/architecture/isa-manual check-html-reference",
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
        print("LinxISA v0.59.1 local release-ready package is current")
        return 0
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
