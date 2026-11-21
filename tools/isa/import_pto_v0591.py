#!/usr/bin/env python3
"""Import the canonical PTO ISA 0.59.1 release into the Linx v0.59 profile."""

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
PROFILE = ROOT / "isa" / "v0.59"
STATE = PROFILE / "state"
LOCK_PATH = PROFILE / "pto-spec.lock.json"

RELEASE = "0.59.1"
PUBLICATION_VERSION = "0.59.1.0"
PUBLICATION_TAG = "v0.59.1.0"
SOURCE_COMMIT = "a89a53d48f5708328be609fe2e6296ac8bdb4bc2"
SOURCE_TREE = "13807a8af41c4481ebcc88bbf33357cda8041f5d"
SOURCE_TAG_OBJECT = "480b4661a6ee5088c7327552b5d66f32d083c83b"
EXPECTED_ABI = "pto-isa-0.59.1-mode-function-v1"
EXPECTED_ENCODING_SHA256 = (
    "d90c881754d66f2cd26f6014d0b582cba88307e70123583d87fc59a918229c28"
)
NUMERIC_VECTOR_BASENAME = "pto-isa-0591-hardware-numeric-vectors.json"

SCALAR_FORM_COUNT = 473
SCOPED_SCALAR_FORM_COUNT = 705
COMMAND_FORM_COUNT = 105
TILE_OPERATION_COUNT = 119
EXTENSION_RESERVATION_COUNT = 50
SYSTEM_REGISTER_COUNT = 100


def load_json(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return document


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
        "scalars": source_root / "spec/catalog/scalar-forms.json",
        "commands": source_root / "spec/catalog/command-forms.json",
        "tiles": source_root / "spec/catalog/tile-operations.json",
        "reservations": (
            source_root / "spec/catalog/extension-encoding-reservations.json"
        ),
        "system_registers": source_root / "spec/catalog/system-registers.json",
        "hardware_profile": source_root / "spec/hardware-conformance-profile.json",
        "numeric_vectors": (
            source_root / "spec/evidence" / NUMERIC_VECTOR_BASENAME
        ),
    }


def git_value(source_root: Path, *arguments: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(source_root), *arguments],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"cannot resolve upstream git identity: {exc}") from exc


def validate_source_git_identity(
    source_root: Path, paths: dict[str, Path]
) -> tuple[str, str]:
    if git_value(source_root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ValueError("upstream PTO checkout must be clean")
    commit = git_value(source_root, "rev-parse", "HEAD")
    tree = git_value(source_root, "rev-parse", "HEAD^{tree}")
    tag_ref = f"refs/tags/{PUBLICATION_TAG}"
    if git_value(source_root, "cat-file", "-t", tag_ref) != "tag":
        raise ValueError(f"upstream publication tag must be annotated: {PUBLICATION_TAG}")
    if git_value(source_root, "rev-parse", tag_ref) != SOURCE_TAG_OBJECT:
        raise ValueError(f"upstream publication tag object is not frozen: {PUBLICATION_TAG}")
    if git_value(source_root, "rev-parse", f"{tag_ref}^{{}}") != commit:
        raise ValueError(f"upstream publication tag does not peel to HEAD: {PUBLICATION_TAG}")
    if commit != SOURCE_COMMIT or tree != SOURCE_TREE:
        raise ValueError(
            "upstream PTO checkout is not the frozen publication identity: "
            f"commit={commit} tree={tree}"
        )
    for path in paths.values():
        relative = path.relative_to(source_root).as_posix()
        try:
            tracked = subprocess.run(
                ["git", "-C", str(source_root), "show", f"{commit}:{relative}"],
                check=True,
                capture_output=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            raise ValueError(f"upstream canonical input is not tracked: {relative}") from exc
        if path.read_bytes() != tracked:
            raise ValueError(f"upstream canonical input differs from {commit}: {relative}")
    return commit, tree


def require_rows(
    document: dict[str, Any], key: str, expected: int, label: str
) -> list[dict[str, Any]]:
    rows = document.get(key)
    if not isinstance(rows, list) or len(rows) != expected:
        actual = len(rows) if isinstance(rows, list) else "missing"
        raise ValueError(f"{label} must contain exactly {expected} rows, got {actual}")
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"{label} rows must be objects")
    return rows


def validate_manifest_inputs(
    manifest: dict[str, Any], source_root: Path, paths: dict[str, Path]
) -> None:
    canonical_inputs = manifest.get("canonical_inputs")
    if not isinstance(canonical_inputs, list):
        raise ValueError("release manifest canonical_inputs must be an array")
    canonical = {
        row.get("path"): row.get("sha256")
        for row in canonical_inputs
        if isinstance(row, dict)
    }
    owned_artifacts = manifest.get("owned_artifacts")
    if not isinstance(owned_artifacts, list):
        raise ValueError("release manifest owned_artifacts must be an array")
    owned = {
        row.get("path"): row.get("sha256")
        for row in owned_artifacts
        if isinstance(row, dict)
    }
    expected_paths = {
        "scalars": "spec/catalog/scalar-forms.json",
        "commands": "spec/catalog/command-forms.json",
        "tiles": "spec/catalog/tile-operations.json",
        "reservations": "spec/catalog/extension-encoding-reservations.json",
        "system_registers": "spec/catalog/system-registers.json",
        "hardware_profile": "spec/hardware-conformance-profile.json",
    }
    for name, relative in expected_paths.items():
        if canonical.get(relative) != sha256(paths[name]):
            raise ValueError(f"{relative} does not match release manifest canonical input")
    if owned.get(f"spec/evidence/{NUMERIC_VECTOR_BASENAME}") != sha256(
        paths["numeric_vectors"]
    ):
        raise ValueError("numeric vectors do not match release manifest owned artifact")


def validate_source(source_root: Path) -> dict[str, dict[str, Any]]:
    paths = source_paths(source_root)
    for path in paths.values():
        if not path.is_file():
            raise ValueError(f"missing upstream PTO source: {path}")
    validate_source_git_identity(source_root, paths)
    docs = {name: load_json(path) for name, path in paths.items()}
    manifest = docs["manifest"]
    if (
        manifest.get("release") != RELEASE
        or manifest.get("publication_version") != PUBLICATION_VERSION
        or manifest.get("encoding_abi") != EXPECTED_ABI
        or manifest.get("encoding_projection_sha256") != EXPECTED_ENCODING_SHA256
    ):
        raise ValueError("upstream PTO identity is not the canonical 0.59.1 contract")
    counts = manifest.get("catalog_counts")
    expected_counts = {
        "scalar_forms": SCALAR_FORM_COUNT,
        "scoped_scalar_forms": SCOPED_SCALAR_FORM_COUNT,
        "command_forms": COMMAND_FORM_COUNT,
        "tile_operations_total": TILE_OPERATION_COUNT,
        "extension_encoding_reservations": EXTENSION_RESERVATION_COUNT,
    }
    if not isinstance(counts, dict) or any(
        counts.get(key) != value for key, value in expected_counts.items()
    ):
        raise ValueError(f"unexpected PTO 0.59.1 catalog counts: {counts}")

    scalars = docs["scalars"]
    if scalars.get("form_count") != SCALAR_FORM_COUNT:
        raise ValueError("scalar form_count does not match the release")
    if scalars.get("scoped_form_count") != SCOPED_SCALAR_FORM_COUNT:
        raise ValueError("scoped Scalar form_count does not match the release")
    scalar_rows = require_rows(scalars, "forms", SCALAR_FORM_COUNT, "Scalar catalog")
    scoped_rows = require_rows(
        scalars, "scoped_forms", SCOPED_SCALAR_FORM_COUNT, "scoped Scalar catalog"
    )
    command_rows = require_rows(
        docs["commands"], "forms", COMMAND_FORM_COUNT, "command catalog"
    )
    tile_rows = require_rows(
        docs["tiles"], "operations", TILE_OPERATION_COUNT, "Tile catalog"
    )
    reservation_rows = require_rows(
        docs["reservations"],
        "reservations",
        EXTENSION_RESERVATION_COUNT,
        "reservation catalog",
    )
    register_rows = require_rows(
        docs["system_registers"],
        "registers",
        SYSTEM_REGISTER_COUNT,
        "system-register catalog",
    )
    if docs["system_registers"].get("register_definition_count") != SYSTEM_REGISTER_COUNT:
        raise ValueError("system-register definition count does not match the release")

    all_forms = [*scalar_rows, *scoped_rows, *command_rows]
    form_ids = [row.get("form_id") for row in all_forms]
    if any(not isinstance(form_id, str) or not form_id for form_id in form_ids):
        raise ValueError("accepted form inventory contains a missing form_id")
    if len(form_ids) != len(set(form_ids)):
        raise ValueError("accepted form IDs are not globally unique")
    scoped_required = {
        "form_id",
        "mnemonic",
        "length_bits",
        "encoding",
        "fields",
        "constraints",
        "operands",
        "base_form_id",
        "inner_length_bits",
        "scope",
        "scope_code",
        "semantic_handler",
    }
    if any(not scoped_required <= row.keys() for row in scoped_rows):
        raise ValueError("scoped Scalar row is missing release identity fields")
    if Counter(row.get("family") for row in tile_rows) != Counter(
        {"TEPL": 79, "TLSU": 28, "CUBE": 12}
    ):
        raise ValueError("unexpected PTO 0.59.1 Tile family counts")
    if Counter(row.get("engine") for row in tile_rows) != Counter(
        {"VEC": 32, "SFU": 47, "TLSU": 28, "CUBE": 12}
    ):
        raise ValueError("unexpected PTO 0.59.1 semantic engine counts")
    if Counter(row.get("semantic_family") for row in command_rows) != Counter(
        {"CMD": 101, "BBD": 4}
    ):
        raise ValueError("unexpected PTO 0.59.1 command family counts")
    if docs["reservations"].get("reservation_count") != len(reservation_rows):
        raise ValueError("reservation_count does not match reservation rows")

    profile = docs["hardware_profile"]
    vectors = docs["numeric_vectors"]
    if (
        profile.get("profile_id") != "pto-hardware-numeric-0.59.1-ieee-v1"
        or profile.get("isa_release") != RELEASE
    ):
        raise ValueError("hardware numeric profile targets another release")
    if (
        vectors.get("hardware_profile_id") != profile.get("profile_id")
        or vectors.get("release") != RELEASE
        or vectors.get("hardware_profile_sha256") != sha256(paths["hardware_profile"])
    ):
        raise ValueError("hardware numeric vectors target another profile")
    validate_manifest_inputs(manifest, source_root, paths)
    return docs


def build_lock(
    source_root: Path, docs: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    paths = source_paths(source_root)
    commit, tree = validate_source_git_identity(source_root, paths)
    manifest = docs["manifest"]
    return {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/pto_spec_lock.v1.json",
        "catalogs": {
            "command_forms": {
                "path": "spec/catalog/command-forms.json",
                "sha256": sha256(paths["commands"]),
                "count": COMMAND_FORM_COUNT,
            },
            "scalar_forms": {
                "path": "spec/catalog/scalar-forms.json",
                "sha256": sha256(paths["scalars"]),
                "count": SCALAR_FORM_COUNT,
                "scoped_count": SCOPED_SCALAR_FORM_COUNT,
            },
            "tile_operations": {
                "path": "spec/catalog/tile-operations.json",
                "sha256": sha256(paths["tiles"]),
                "count": TILE_OPERATION_COUNT,
            },
            "extension_encoding_reservations": {
                "path": "spec/catalog/extension-encoding-reservations.json",
                "sha256": sha256(paths["reservations"]),
                "count": EXTENSION_RESERVATION_COUNT,
            },
            "system_registers": {
                "path": "spec/catalog/system-registers.json",
                "sha256": sha256(paths["system_registers"]),
                "count": SYSTEM_REGISTER_COUNT,
            },
        },
        "content_sha256": manifest["content_sha256"],
        "encoding_abi": EXPECTED_ABI,
        "encoding_projection_sha256": EXPECTED_ENCODING_SHA256,
        "hardware_conformance_profile": {
            "path": "spec/hardware-conformance-profile.json",
            "profile_id": docs["hardware_profile"]["profile_id"],
            "sha256": sha256(paths["hardware_profile"]),
        },
        "numeric_conformance_vectors": {
            "path": f"spec/evidence/{NUMERIC_VECTOR_BASENAME}",
            "sha256": sha256(paths["numeric_vectors"]),
        },
        "publication": {
            "tag": PUBLICATION_TAG,
            "tag_object": SOURCE_TAG_OBJECT,
            "version": PUBLICATION_VERSION,
            "release_url": (
                f"https://github.com/PTO-ISA/pto-spec/releases/tag/{PUBLICATION_TAG}"
            ),
        },
        "release": RELEASE,
        "specification_status": manifest["specification_status"],
        "release_manifest": {
            "path": "spec/release-manifest.json",
            "sha256": sha256(paths["manifest"]),
        },
        "source": {
            "commit": commit,
            "tree": tree,
            "repository": "https://github.com/PTO-ISA/pto-spec.git",
        },
    }


def locked_projection(document: dict[str, Any]) -> dict[str, Any]:
    result = dict(document)
    result["source_lock"] = "isa/v0.59/pto-spec.lock.json"
    return result


def projections(docs: dict[str, dict[str, Any]]) -> dict[Path, dict[str, Any]]:
    return {
        STATE / "pto_scalar_forms.json": locked_projection(docs["scalars"]),
        STATE / "pto_command_forms.json": locked_projection(docs["commands"]),
        STATE / "pto_tile_operations.json": locked_projection(docs["tiles"]),
        STATE / "extension_encoding_reservations.json": locked_projection(
            docs["reservations"]
        ),
        STATE / "pto_system_registers.json": locked_projection(
            docs["system_registers"]
        ),
        STATE / "pto_hardware_conformance_profile.json": locked_projection(
            docs["hardware_profile"]
        ),
        STATE / "pto_hardware_numeric_vectors.json": locked_projection(
            docs["numeric_vectors"]
        ),
    }


def compare_or_write(
    expected: dict[Path, dict[str, Any]], check: bool
) -> list[str]:
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
        source_root = args.source_root.resolve()
        docs = validate_source(source_root)
        lock = build_lock(source_root, docs)
        if args.update_lock:
            LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
            LOCK_PATH.write_text(pretty(lock), encoding="utf-8")
        elif not LOCK_PATH.is_file() or load_json(LOCK_PATH) != lock:
            raise ValueError(
                "checked-in isa/v0.59/pto-spec.lock.json does not match the "
                "upstream release; rerun with --update-lock"
            )
        errors = compare_or_write(projections(docs), args.check)
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    action = "verified" if args.check else "updated"
    print(
        f"{action} PTO ISA {RELEASE} lock and exact Linx v0.59 input projections"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
