#!/usr/bin/env python3
"""Verify immutable v0.59.1 artifacts after extending the profile registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TAG = "v0.59.1"
IMMUTABLE = (
    "isa/v0.59/linxisa-v0.59.json",
    "isa/v0.59/meta.json",
    "isa/v0.59/release_manifest.json",
    "isa/v0.59/release_package.json",
)


def tagged(path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{TAG}:{path}"], cwd=ROOT
    )


def load_bytes(data: bytes, path: str) -> dict[str, Any]:
    value = json.loads(data)
    if not isinstance(value, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return value


def check() -> list[str]:
    errors: list[str] = []
    for relative in IMMUTABLE:
        path = ROOT / relative
        try:
            expected = tagged(relative)
        except subprocess.CalledProcessError as error:
            errors.append(f"unable to read {relative} from {TAG}: {error}")
            continue
        if not path.is_file() or path.read_bytes() != expected:
            errors.append(f"immutable {TAG} artifact changed: {relative}")

    try:
        frozen = load_bytes(tagged("isa/profile-selection.json"), "tagged selection")
        current = load_bytes(
            (ROOT / "isa/profile-selection.json").read_bytes(), "current selection"
        )
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        errors.append(f"unable to validate profile registry compatibility: {error}")
        return errors

    for key in ("schema", "default_profile", "policy"):
        if current.get(key) != frozen.get(key):
            errors.append(f"profile registry changed historical field: {key}")
    frozen_profiles = frozen.get("profiles")
    current_profiles = current.get("profiles")
    if not isinstance(frozen_profiles, dict) or not isinstance(current_profiles, dict):
        errors.append("profile registry profiles must be mappings")
    else:
        for name, expected in frozen_profiles.items():
            if current_profiles.get(name) != expected:
                errors.append(f"profile registry changed historical profile: {name}")
    return errors


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    errors = check()
    if errors:
        for error in errors:
            print(error)
        return 1
    print("OK: immutable v0.59.1 artifacts and historical profiles are unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
