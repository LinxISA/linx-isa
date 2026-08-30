#!/usr/bin/env python3
"""Validate exact PTO producer, SuperscalarModel consumer, and artifact locks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCK = ROOT / "isa/v0.58/pto-functional-model.lock.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gitlink(root: Path, path: str) -> str:
    result = subprocess.run(
        ["git", "ls-files", "-s", "--", path],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    fields = result.stdout.strip().split()
    if result.returncode != 0 or len(fields) < 4 or fields[0] != "160000":
        raise ValueError(f"{path} is not an indexed gitlink")
    return fields[1]


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} root is not an object")
    return value


def validate(
    root: Path,
    lock_path: Path,
    descriptor: Path | None,
    corpus: Path | None,
) -> None:
    lock = load_json(lock_path)
    if lock.get("schema_version") != 1 or lock.get("release") != "0.58.5":
        raise ValueError("functional-model lock schema/release mismatch")
    architecture = lock.get("architecture")
    model = lock.get("model")
    interfaces = lock.get("interfaces")
    corpus_lock = lock.get("corpus")
    if not all(isinstance(item, dict) for item in (
        architecture, model, interfaces, corpus_lock
    )):
        raise ValueError("functional-model lock sections are malformed")

    architecture = architecture  # type: ignore[assignment]
    model = model  # type: ignore[assignment]
    interfaces = interfaces  # type: ignore[assignment]
    corpus_lock = corpus_lock  # type: ignore[assignment]
    if gitlink(root, str(architecture["path"])) != architecture["commit"]:
        raise ValueError("PTO producer gitlink mismatch")
    if gitlink(root, str(model["path"])) != model["commit"]:
        raise ValueError("SuperscalarModel consumer gitlink mismatch")

    pto_lock_path = root / str(architecture["pto_lock"])
    if sha256(pto_lock_path) != architecture["pto_lock_sha256"]:
        raise ValueError("PTO architecture lock hash mismatch")
    pto_lock = load_json(pto_lock_path)
    if pto_lock.get("source") != {
        "commit": architecture["commit"],
        "tree": architecture["tree"],
        "repository": architecture["repository"],
    }:
        raise ValueError("PTO architecture lock source mismatch")
    release_manifest = root / str(architecture["path"]) / "spec/release-manifest.json"
    if sha256(release_manifest) != architecture["release_manifest_sha256"]:
        raise ValueError("PTO release manifest hash mismatch")

    model_ndf = root / str(model["path"]) / str(model["ndf"])
    if sha256(model_ndf) != model["ndf_sha256"]:
        raise ValueError("SuperscalarModel NDF hash mismatch")

    if descriptor is not None:
        descriptor_document = load_json(descriptor)
        if sha256(descriptor) != interfaces["model_descriptor_sha256"]:
            raise ValueError("model descriptor hash mismatch")
        if descriptor_document.get("source") != {
            "pto_commit": architecture["commit"],
            "pto_tree": architecture["tree"],
        }:
            raise ValueError("model descriptor PTO source mismatch")
        descriptor_interfaces = descriptor_document.get("interfaces")
        for key in (
            "experimental_c_abi_version",
            "snapshot_schema",
            "snapshot_schema_version",
            "bundle_tile_summary_schema",
        ):
            if not isinstance(descriptor_interfaces, dict) or (
                descriptor_interfaces.get(key) != interfaces[key]
            ):
                raise ValueError(f"model descriptor {key} mismatch")
        if (descriptor_document.get("model") or {}).get("pto_mir_schema") != (
            interfaces["pto_mir_schema"]
        ):
            raise ValueError("model descriptor MIR schema mismatch")

    if corpus is not None:
        manifest = corpus / "manifest.json" if corpus.is_dir() else corpus
        corpus_document = load_json(manifest)
        if sha256(manifest) != corpus_lock["manifest_sha256"]:
            raise ValueError("functional-model corpus hash mismatch")
        if corpus_document.get("schema") != corpus_lock["schema"]:
            raise ValueError("functional-model corpus schema mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--descriptor", type=Path)
    parser.add_argument("--corpus", type=Path)
    arguments = parser.parse_args()
    try:
        validate(
            arguments.root.resolve(),
            arguments.lock.resolve(),
            arguments.descriptor.resolve() if arguments.descriptor else None,
            arguments.corpus.resolve() if arguments.corpus else None,
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"PTO functional-model lock failed: {error}", file=sys.stderr)
        return 1
    print("PTO functional-model lock passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
