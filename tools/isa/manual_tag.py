#!/usr/bin/env python3
"""Read the current v0.59.1 manual revision without tag fallback.

``RELEASE_TAG`` and ``SIGNED_TAG_COMMIT`` identify the original signed release.
The HTML reference itself is rebuilt from the current working-tree revision;
missing sources fail closed instead of being silently recovered from the tag.
"""

from __future__ import annotations
from functools import lru_cache
import json, subprocess
from pathlib import Path
from typing import Any

RELEASE_TAG = "v0.59.1"
SIGNED_TAG_COMMIT = "d262515b55c727073997c8f4c95261909f2fe8d3"
REPO_ROOT = Path(__file__).resolve().parents[2]
REVISION_COMMIT = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
).strip()
# Compatibility name used by HTML-only helpers for source provenance.
REVIEWED_COMMIT = REVISION_COMMIT


@lru_cache(maxsize=1)
def verified_tag_commit() -> str:
    result = subprocess.run(
        ["git", "rev-list", "-n", "1", f"refs/tags/{RELEASE_TAG}^{{commit}}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    commit = result.stdout.strip()
    if commit != SIGNED_TAG_COMMIT:
        raise ValueError(
            f"{RELEASE_TAG} resolves to {commit or '<missing>'}, expected signed {SIGNED_TAG_COMMIT}"
        )
    return commit


@lru_cache(maxsize=1)
def revision_commit() -> str:
    return REVISION_COMMIT


@lru_cache(maxsize=None)
def tagged_bytes(path: str) -> bytes:
    """Compatibility reader for the current v0.59.1 revision."""
    source = REPO_ROOT / path
    if not source.is_file():
        raise FileNotFoundError(f"v0.59.1 revision source is missing: {path}")
    return source.read_bytes()


@lru_cache(maxsize=None)
def tagged_json(path: str) -> dict[str, Any]:
    return json.loads(tagged_bytes(path).decode("utf-8"))


__all__ = [
    "RELEASE_TAG",
    "REVIEWED_COMMIT",
    "SIGNED_TAG_COMMIT",
    "REVISION_COMMIT",
    "verified_tag_commit",
    "revision_commit",
    "tagged_bytes",
    "tagged_json",
]
