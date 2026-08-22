#!/usr/bin/env python3
"""Validate exact PTO profile-hook provenance and the concrete Linx mapping."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


LOCK_PATH = Path("isa/v0.58/pto-profile-hooks.lock.json")
EXPECTED_PROFILE_ID = "PTO-ARCH-EXTENSION-FIRST-USE-PROFILE-001"
EXPECTED_REPOSITORY = "https://github.com/PTO-ISA/pto-spec.git"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(encoded)


def git_value(repository: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def check(root: Path, pto_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    lock_file = root / LOCK_PATH
    if not lock_file.is_file():
        return [f"missing PTO profile-hook lock: {lock_file}"]
    lock = json.loads(lock_file.read_text(encoding="utf-8"))
    hook = (lock.get("profile_hooks") or {}).get("extension_first_use") or {}
    source = hook.get("source") or {}

    if lock.get("common_pto_release") != "0.58.3":
        errors.append("common PTO release must remain 0.58.3")
    common_lock_path = root / str(lock.get("common_pto_lock") or "")
    if not common_lock_path.is_file():
        errors.append(f"common PTO lock is missing: {common_lock_path}")
    else:
        common_sha = sha256_bytes(common_lock_path.read_bytes())
        if common_sha != lock.get("common_pto_lock_sha256"):
            errors.append("common PTO lock SHA-256 mismatch")
        common = json.loads(common_lock_path.read_text(encoding="utf-8"))
        if common.get("release") != "0.58.3":
            errors.append("common PTO lock release changed")

    if hook.get("profile_id") != EXPECTED_PROFILE_ID:
        errors.append("extension first-use profile ID mismatch")
    if source.get("repository") != EXPECTED_REPOSITORY:
        errors.append("extension first-use repository mismatch")
    mapping_path = root / str(hook.get("linx_mapping_path") or "")
    if not mapping_path.is_file():
        errors.append(f"Linx mapping source is missing: {mapping_path}")
    else:
        mapping_document = json.loads(mapping_path.read_text(encoding="utf-8"))
        mapping_key = str(hook.get("linx_mapping_key") or "")
        mapping = mapping_document.get(mapping_key)
        if mapping is None:
            errors.append(f"Linx mapping key is missing: {mapping_key}")
        elif canonical_sha256(mapping) != hook.get("linx_mapping_sha256"):
            errors.append("Linx mapping SHA-256 mismatch")

    if pto_root is not None:
        pto_root = pto_root.resolve()
        try:
            commit = git_value(pto_root, "rev-parse", "HEAD")
            tree = git_value(pto_root, "show", "-s", "--format=%T", "HEAD")
        except subprocess.CalledProcessError as error:
            errors.append(f"PTO checkout is not a readable git repository: {error}")
        else:
            if commit != source.get("commit"):
                errors.append(f"PTO profile-hook commit mismatch: {commit}")
            if tree != source.get("tree"):
                errors.append(f"PTO profile-hook tree mismatch: {tree}")
        hook_file = pto_root / str(source.get("path") or "")
        if not hook_file.is_file():
            errors.append(f"PTO profile-hook source is missing: {hook_file}")
        elif sha256_bytes(hook_file.read_bytes()) != source.get("sha256"):
            errors.append("PTO profile-hook source SHA-256 mismatch")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--pto-root", type=Path)
    arguments = parser.parse_args()
    errors = check(arguments.root.resolve(), arguments.pto_root)
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print("OK: PTO profile-hook lock matches the Linx first-use contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
