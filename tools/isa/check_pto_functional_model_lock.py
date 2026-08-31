#!/usr/bin/env python3
"""Validate exact PTO architecture, ASLRef model, and gfrun consumer pins."""

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


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} root is not an object")
    return value


def gitlink(root: Path, path: str) -> str:
    completed = subprocess.run(
        ["git", "ls-files", "-s", "--", path],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    fields = completed.stdout.strip().split()
    if completed.returncode != 0 or len(fields) < 4 or fields[0] != "160000":
        raise ValueError(f"{path} is not an indexed gitlink")
    return fields[1]


def checkout_value(root: Path, path: str, revision: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root / path), "rev-parse", revision],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError(f"cannot inspect initialized submodule {path}")
    return completed.stdout.strip()


def validate_component(root: Path, section: dict[str, object], label: str) -> None:
    path = str(section["path"])
    commit = str(section["commit"])
    if gitlink(root, path) != commit:
        raise ValueError(f"{label} gitlink mismatch")
    if (root / path / ".git").exists():
        if checkout_value(root, path, "HEAD") != commit:
            raise ValueError(f"{label} checkout mismatch")
        if checkout_value(root, path, "HEAD^{tree}") != section["tree"]:
            raise ValueError(f"{label} tree mismatch")


def validate(root: Path, lock_path: Path) -> None:
    lock = load_json(lock_path)
    if lock.get("schema_version") != 1 or lock.get("release") != "0.58.5":
        raise ValueError("functional-model lock schema/release mismatch")
    architecture = lock.get("architecture")
    reference_model = lock.get("reference_model")
    consumer = lock.get("consumer")
    aslref = lock.get("aslref")
    interfaces = lock.get("interfaces")
    if not all(isinstance(item, dict) for item in (
        architecture, reference_model, consumer, aslref, interfaces
    )):
        raise ValueError("functional-model lock sections are malformed")

    architecture = architecture  # type: ignore[assignment]
    reference_model = reference_model  # type: ignore[assignment]
    consumer = consumer  # type: ignore[assignment]
    aslref = aslref  # type: ignore[assignment]
    interfaces = interfaces  # type: ignore[assignment]
    validate_component(root, architecture, "PTO architecture")
    validate_component(root, reference_model, "ASL reference model")
    validate_component(root, consumer, "SuperScalarModel consumer")

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
    release_manifest = (
        root / str(architecture["path"]) / "spec/release-manifest.json"
    )
    if sha256(release_manifest) != architecture["release_manifest_sha256"]:
        raise ValueError("PTO release manifest hash mismatch")

    model_lock_path = (
        root / str(reference_model["path"]) / str(reference_model["model_lock"])
    )
    if sha256(model_lock_path) != reference_model["model_lock_sha256"]:
        raise ValueError("ASL model lock hash mismatch")
    model_lock = load_json(model_lock_path)
    expected_model_fields = {
        "pto_commit": architecture["commit"],
        "pto_tree": architecture["tree"],
        "aslref_commit": aslref["commit"],
        "model_abi": interfaces["model_abi"],
        "worker_protocol": interfaces["worker_protocol"],
        "architecture_version": interfaces["architecture_version"],
    }
    for field, expected in expected_model_fields.items():
        if model_lock.get(field) != expected:
            raise ValueError(f"ASL model lock {field} mismatch")

    for section, field in (
        (reference_model, "model_ndf"),
        (consumer, "modeling_spec"),
    ):
        component_root = root / str(section["path"])
        path = component_root / str(section[field])
        if (component_root / ".git").exists() and not path.is_file():
            raise ValueError(f"missing locked contract: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    arguments = parser.parse_args()
    try:
        validate(arguments.root.resolve(), arguments.lock.resolve())
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"PTO functional-model lock failed: {error}", file=sys.stderr)
        return 1
    print("PTO functional-model lock passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
