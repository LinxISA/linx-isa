#!/usr/bin/env python3
"""Read immutable LinxISA manual authority from the reviewed release tag."""

from __future__ import annotations
from functools import lru_cache
import json, subprocess
from pathlib import Path
from typing import Any

RELEASE_TAG = "v0.59.1"
REVIEWED_COMMIT = "d262515b55c727073997c8f4c95261909f2fe8d3"
REPO_ROOT = Path(__file__).resolve().parents[2]


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
    if commit != REVIEWED_COMMIT:
        raise ValueError(
            f"{RELEASE_TAG} resolves to {commit or '<missing>'}, expected reviewed {REVIEWED_COMMIT}"
        )
    return commit


@lru_cache(maxsize=None)
def tagged_bytes(path: str) -> bytes:
    commit = verified_tag_commit()
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return result.stdout


@lru_cache(maxsize=None)
def tagged_json(path: str) -> dict[str, Any]:
    return json.loads(tagged_bytes(path).decode("utf-8"))


__all__ = [
    "RELEASE_TAG",
    "REVIEWED_COMMIT",
    "verified_tag_commit",
    "tagged_bytes",
    "tagged_json",
]
