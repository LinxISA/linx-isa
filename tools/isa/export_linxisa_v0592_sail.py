#!/usr/bin/env python3
"""Export and verify the LinxISA v0.59.2 Sail and release packages."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "isa/sail"
PROFILE = ROOT / "isa/v0.59.2"
SPEC = PROFILE / "linxisa-v0.59.2.json"
MANIFEST_PATH = PROFILE / "release_manifest.json"
LOCK = ROOT / "isa/v0.59/pto-spec.lock.json"
RELEASE_PACKAGE = PROFILE / "release_package.json"
TOOLCHAIN = ROOT / "isa/sail/toolchain.json"
ENTRY_TEXT = """// Generated LinxISA v0.59.2 published specification entry.
// Decoding and execution remain compatible with the v0.59.1 model.
// The catalog marks 193 forms obsolete. Legacy execution policy remains a
// separate architecture decision; this package preserves v0.59.1 execution.

$include "linxisa.sail"
$include "execute/v0591_candidate_dispatch.sail"
"""
SAIL_MANIFEST = "linxisa-v0592-sail-package.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return value


def render(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def obsolete_rows(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in catalog["instructions"]
        if row.get("architecture_status", {}).get("state") == "obsolete"
    ]
    if len(rows) != 193:
        raise ValueError(f"expected 193 obsolete forms, found {len(rows)}")
    return rows


def package_files(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name not in {SAIL_MANIFEST, "SHA256SUMS"}
    }


def run_generator(output: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/isa/gen_sail_decode.py"),
            "--spec",
            str(SPEC),
            "--out",
            str(output / "model/decode/decode.sail"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(
            result.stderr or result.stdout or "Sail decoder generation failed"
        )


def export(output: Path) -> dict[str, Any]:
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    catalog = load(SPEC)
    lock = load(LOCK)
    obsolete = obsolete_rows(catalog)
    shutil.copytree(SOURCE, output)
    run_generator(output)
    entry = output / "model/linxisa_v0592.sail"
    entry.write_text(ENTRY_TEXT, encoding="utf-8")
    files = package_files(output)
    package = {
        "schema": "linxisa.sail-package.v1",
        "profile": "v0.59.2",
        "version": "0.59.2",
        "state": "published-specification",
        "entry": "model/linxisa_v0592.sail",
        "catalog": {
            "path": "isa/v0.59.2/linxisa-v0.59.2.json",
            "sha256": sha256(SPEC),
            "instruction_count": catalog["instruction_count"],
            "obsolete_form_count": len(obsolete),
        },
        "identity": {
            "encoding_abi": lock["encoding_abi"],
            "encoding_projection_sha256": lock["encoding_projection_sha256"],
            "pto_release": lock["release"],
            "linxisa_release": "0.59.2",
        },
        "execution_compatibility": {
            "base": "LinxISA-v0.59.1",
            "obsolete_forms_decode": True,
            "obsolete_forms_execute_with_v0591_semantics": True,
            "obsolete_trap_policy_decided": False,
        },
        "toolchain": load(TOOLCHAIN),
        "files": files,
        "files_sha256": canonical_sha256(files),
    }
    (output / SAIL_MANIFEST).write_text(render(package), encoding="utf-8")
    (output / "SHA256SUMS").write_text(
        "\n".join(f"{digest}  {path}" for path, digest in files.items()) + "\n",
        encoding="utf-8",
    )
    return package


def check(output: Path) -> None:
    package = load(output / SAIL_MANIFEST)
    if package.get("schema") != "linxisa.sail-package.v1":
        raise ValueError("Sail package has the wrong schema")
    if package.get("entry") != "model/linxisa_v0592.sail":
        raise ValueError("Sail package has the wrong canonical entry")
    if (output / package["entry"]).read_text(encoding="utf-8") != ENTRY_TEXT:
        raise ValueError("Sail package entry is stale")
    files = package_files(output)
    if package.get("files") != files or package.get("files_sha256") != canonical_sha256(
        files
    ):
        raise ValueError("Sail package file hashes are stale")
    sums = "\n".join(f"{digest}  {path}" for path, digest in files.items()) + "\n"
    if (output / "SHA256SUMS").read_text(encoding="utf-8") != sums:
        raise ValueError("Sail package checksums are stale")
    with tempfile.TemporaryDirectory(
        prefix="linx-sail-v0592-export-check-"
    ) as directory:
        expected = Path(directory) / "sail"
        expected_package = export(expected)
        expected_files = package_files(expected)
    if files != expected_files or package != expected_package:
        raise ValueError("Sail package or manifest differs from a fresh export")


def release_inputs() -> tuple[str, ...]:
    sail_sources = tuple(
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "isa/sail/model").rglob("*"))
        if path.is_file() and path.suffix in {".sail", ".sail_project"}
    )
    inputs = (
        "isa/v0.59.2/linxisa-v0.59.2.json",
        "isa/v0.59.2/release_manifest.json",
        "isa/v0.59/pto-spec.lock.json",
        "isa/v0.59/linxisa-v0.59.json",
        "isa/v0.59/state/extension_encoding_reservations.json",
        "isa/sail/toolchain.json",
        "docs/architecture/linx-two-level-block-obsolescence.md",
        "tools/isa/build_linxisa_v0592_catalog.py",
        "tools/isa/build_linxisa_v0592_release_prep.py",
        "tools/isa/check_v0592_sail.py",
        "tools/isa/export_linxisa_v0592_sail.py",
        "tools/isa/gen_sail_decode.py",
        *sail_sources,
    )
    return tuple(dict.fromkeys(inputs))


def release_package() -> dict[str, Any]:
    catalog = load(SPEC)
    manifest = load(MANIFEST_PATH)
    lock = load(LOCK)
    obsolete = obsolete_rows(catalog)
    inputs = {relative: sha256(ROOT / relative) for relative in release_inputs()}
    if manifest.get("version") != "0.59.2":
        raise ValueError("v0.59.2 release manifest is stale")
    if manifest["catalog"]["sha256"] != sha256(SPEC):
        raise ValueError("release manifest does not bind the v0.59.2 catalog")
    return {
        "schema": "linxisa.release-package.v1",
        "profile": "v0.59.2",
        "version": "0.59.2",
        "state": "published-specification",
        "publication_allowed": True,
        "default_profile": "v0.58",
        "identity": {
            "encoding_abi": lock["encoding_abi"],
            "encoding_projection_sha256": lock["encoding_projection_sha256"],
            "pto_release": lock["release"],
            "linxisa_release": "0.59.2",
        },
        "catalog": {
            **manifest["catalog"],
            "instruction_count": catalog["instruction_count"],
            "obsolete_form_count": len(obsolete),
        },
        "sail": {
            "entry": "model/linxisa_v0592.sail",
            "exporter": "tools/isa/export_linxisa_v0592_sail.py",
            "source_dispatch": "isa/sail/model/execute/v0591_candidate_dispatch.sail",
            "toolchain": load(TOOLCHAIN),
            "state": "v0591-compatible-execution-with-v0592-catalog-status",
        },
        "obsolete_policy": {
            "form_count": len(obsolete),
            "encodings_remain_reserved": True,
            "assembler_emission_policy": "not-defined-by-this-release",
            "binary_trap_policy": "not-decided",
            "sail_execution": "v0.59.1-compatible",
        },
        "inputs": inputs,
        "inputs_sha256": canonical_sha256(inputs),
        "upstream_source_hashes": {
            "scalar_forms": lock["catalogs"]["scalar_forms"],
            "command_forms": lock["catalogs"]["command_forms"],
            "tile_operations": lock["catalogs"]["tile_operations"],
            "extension_encoding_reservations": lock["catalogs"][
                "extension_encoding_reservations"
            ],
        },
        "qualification": {
            "release_qualified": manifest["qualification"]["release_qualified"],
            "specification_qualified": manifest["qualification"][
                "specification_qualified"
            ],
            "encoding_qualified": manifest["qualification"]["encoding_qualified"],
            "sail_package_qualified": manifest["qualification"][
                "sail_package_qualified"
            ],
            "linux_qualified": manifest["qualification"]["linux_qualified"],
            "leaf_components_qualified": manifest["qualification"][
                "leaf_components_qualified"
            ],
            "system_runtime_qualified": manifest["qualification"][
                "system_runtime_qualified"
            ],
            "platform_qualified": manifest["qualification"]["platform_qualified"],
            "scope": manifest["qualification"]["qualification_scope"],
            "evidence": {
                "catalog_builder": "tools/isa/build_linxisa_v0592_catalog.py --check",
                "encoding_validator": "tools/isa/validate_spec.py --profile v0.59.2",
                "sail_validator": "tools/isa/check_v0592_sail.py",
                "release_package_validator": "tools/isa/export_linxisa_v0592_sail.py --check-release-package",
            },
            "remaining": manifest["qualification"]["remaining_platform_qualification"],
        },
        "required_checks": [
            "python3 tools/isa/build_linxisa_v0592_catalog.py --check",
            "python3 tools/isa/export_linxisa_v0592_sail.py --check-release-package",
            "python3 tools/isa/check_v0592_sail.py",
        ],
    }


def write_or_check_release_package(*, check_only: bool) -> None:
    expected = render(release_package())
    if check_only:
        if (
            not RELEASE_PACKAGE.is_file()
            or RELEASE_PACKAGE.read_text(encoding="utf-8") != expected
        ):
            raise ValueError("v0.59.2 release package is stale")
        return
    RELEASE_PACKAGE.write_text(expected, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--output", type=Path)
    modes.add_argument("--check", type=Path)
    modes.add_argument("--write-release-package", action="store_true")
    modes.add_argument("--check-release-package", action="store_true")
    args = parser.parse_args()
    try:
        if args.output is not None:
            package = export(args.output.resolve())
            print(
                json.dumps(
                    {"output": str(args.output.resolve()), **package}, sort_keys=True
                )
            )
        elif args.check is not None:
            check(args.check.resolve())
            print(f"LinxISA v0.59.2 Sail package is current: {args.check.resolve()}")
        else:
            write_or_check_release_package(check_only=args.check_release_package)
            action = "current" if args.check_release_package else "written"
            print(f"LinxISA v0.59.2 release package is {action}: {RELEASE_PACKAGE}")
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"v0.59.2 Sail export failed: {error}") from error
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
