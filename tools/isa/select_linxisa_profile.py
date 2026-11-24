#!/usr/bin/env python3
"""Resolve a LinxISA profile without silently changing the platform default."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_selection(root: Path = ROOT) -> dict:
    selection = json.loads((root / "isa/profile-selection.json").read_text(encoding="utf-8"))
    if not isinstance(selection, dict):
        raise ValueError("profile selection must be a JSON object")
    return selection


def resolve_profile(
    profile: str | None = None,
    *,
    allow_prepublication: bool = False,
    require_release_qualified: bool = False,
    root: Path = ROOT,
) -> dict:
    selection = load_selection(root)
    selected = profile or selection["default_profile"]
    row = selection["profiles"][selected]
    if row["state"] == "selectable-prepublication" and not allow_prepublication:
        raise ValueError(
            f"{selected} is prepublication; pass --allow-prepublication explicitly"
        )
    if require_release_qualified and not row.get("release_qualified", False):
        raise ValueError(f"{selected} is not release-qualified")
    return {"profile": selected, **row}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("v0.58", "v0.59"))
    parser.add_argument("--allow-prepublication", action="store_true")
    parser.add_argument("--require-release-qualified", action="store_true")
    args = parser.parse_args()
    try:
        selected = resolve_profile(
            args.profile,
            allow_prepublication=args.allow_prepublication,
            require_release_qualified=args.require_release_qualified,
        )
    except (KeyError, OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
    print(json.dumps(selected, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
