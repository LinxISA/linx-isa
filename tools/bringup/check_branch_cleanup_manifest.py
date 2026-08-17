#!/usr/bin/env python3
"""Validate exact branch-cleanup evidence without deleting any refs."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


OID_RE = re.compile(r"^[0-9a-f]{40}$")
SCOPES = {"local", "remote", "tag"}
ACTIONS = {"delete", "retain"}
MODES = {"static", "pre-delete", "post-delete"}
REQUIRED_FIELDS = {
    "repository",
    "scope",
    "ref",
    "oid",
    "action",
    "classification",
    "evidence",
    "required_integration_commit",
    "attached_worktree_prohibited",
    "pre_state",
    "post_state",
}


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def _resolve_ref(root: Path, entry: dict[str, Any]) -> str | None:
    scope = entry["scope"]
    ref = entry["ref"]
    if scope == "local":
        result = _git(root, "show-ref", "--verify", "--hash", f"refs/heads/{ref}")
        return result.stdout.strip() if result.returncode == 0 else None
    if scope == "tag":
        result = _git(root, "rev-parse", "--verify", f"refs/tags/{ref}^{{commit}}")
        return result.stdout.strip() if result.returncode == 0 else None
    remote = entry.get("remote", "origin")
    result = _git(root, "ls-remote", "--heads", remote, ref)
    if result.returncode:
        return None
    expected_name = f"refs/heads/{ref}"
    for line in result.stdout.splitlines():
        oid, name = line.split(maxsplit=1)
        if name == expected_name:
            return oid
    return None


def _attached_branches(root: Path) -> set[str]:
    result = _git(root, "worktree", "list", "--porcelain")
    branches: set[str] = set()
    for line in result.stdout.splitlines():
        if line.startswith("branch refs/heads/"):
            branches.add(line.removeprefix("branch refs/heads/"))
    return branches


def _object_exists(root: Path, oid: str) -> bool:
    return _git(root, "cat-file", "-e", f"{oid}^{{commit}}").returncode == 0


def _is_ancestor_of_head(root: Path, oid: str) -> bool:
    return _git(root, "merge-base", "--is-ancestor", oid, "HEAD").returncode == 0


def validate_static(root: Path, manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != "linx-branch-cleanup-v1":
        errors.append("manifest schema must be linx-branch-cleanup-v1")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        return errors + ["manifest entries must be a non-empty list"]

    seen: set[tuple[str, str, str, str]] = set()
    for index, entry in enumerate(entries):
        label = f"entry[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = REQUIRED_FIELDS - entry.keys()
        if missing:
            errors.append(f"{label} missing fields: {', '.join(sorted(missing))}")
            continue
        if entry["repository"] != ".":
            errors.append(f"{label} repository must be '.' for this manifest")
        if entry["scope"] not in SCOPES:
            errors.append(f"{label} has invalid scope: {entry['scope']}")
        if entry["action"] not in ACTIONS:
            errors.append(f"{label} has invalid action: {entry['action']}")
        if not isinstance(entry["ref"], str) or not entry["ref"]:
            errors.append(f"{label} ref must be a non-empty string")
        if not isinstance(entry["oid"], str) or not OID_RE.fullmatch(entry["oid"]):
            errors.append(f"{label} oid must be a full lowercase Git OID")
        integration = entry["required_integration_commit"]
        if not isinstance(integration, str) or not OID_RE.fullmatch(integration):
            errors.append(f"{label} required integration commit must be a full Git OID")
        elif not _object_exists(root, integration):
            errors.append(f"{label} required integration commit is unavailable: {integration}")
        elif not _is_ancestor_of_head(root, integration):
            errors.append(
                f"{label} required integration commit must be an ancestor of HEAD: "
                f"{integration}"
            )
        if not isinstance(entry["attached_worktree_prohibited"], bool):
            errors.append(f"{label} attached_worktree_prohibited must be boolean")
        if entry["action"] == "delete" and not entry["attached_worktree_prohibited"]:
            errors.append(f"{label} delete action must prohibit attached worktrees")
        for state_name in ("pre_state", "post_state"):
            state = entry[state_name]
            if not isinstance(state, dict) or not isinstance(state.get("expected_present"), bool):
                errors.append(f"{label} {state_name} must contain boolean expected_present")
        evidence = entry["evidence"]
        if not isinstance(evidence, dict):
            errors.append(f"{label} evidence must be an object")
        else:
            for field in ("kind", "replacement_oid", "summary"):
                if not isinstance(evidence.get(field), str) or not evidence[field]:
                    errors.append(f"{label} evidence.{field} must be a non-empty string")
            replacement = evidence.get("replacement_oid", "")
            if isinstance(replacement, str) and OID_RE.fullmatch(replacement):
                if evidence.get("kind") != "retention-policy":
                    if not _object_exists(root, replacement):
                        errors.append(f"{label} replacement OID is unavailable: {replacement}")
                    elif not _is_ancestor_of_head(root, replacement):
                        errors.append(
                            f"{label} replacement OID must be an ancestor of HEAD: "
                            f"{replacement}"
                        )
            else:
                errors.append(f"{label} evidence.replacement_oid must be a full Git OID")
        key = (entry["repository"], entry["scope"], entry.get("remote", ""), entry["ref"])
        if key in seen:
            errors.append(f"{label} duplicates ref identity: {key}")
        seen.add(key)
    return errors


def validate_state(root: Path, manifest: dict[str, Any], mode: str) -> list[str]:
    errors: list[str] = []
    attached = _attached_branches(root)
    state_name = "pre_state" if mode == "pre-delete" else "post_state"
    for entry in manifest["entries"]:
        actual = _resolve_ref(root, entry)
        expected_present = entry[state_name]["expected_present"]
        label = f"{entry['scope']} {entry['ref']}"
        if expected_present and actual is None:
            errors.append(f"{label}: expected present in {mode}")
            continue
        if not expected_present and actual is not None:
            errors.append(f"{label}: expected absent in {mode}, found {actual}")
            continue
        if actual is not None and actual != entry["oid"]:
            errors.append(f"{label}: OID mismatch; expected {entry['oid']}, found {actual}")
        if (
            mode == "pre-delete"
            and entry["action"] == "delete"
            and entry["scope"] == "local"
            and entry["attached_worktree_prohibited"]
            and entry["ref"] in attached
        ):
            errors.append(f"{label}: delete ref has an attached worktree")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--mode", choices=sorted(MODES), default="static")
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    root = Path.cwd().resolve()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: invalid cleanup manifest: {exc}", file=sys.stderr)
        return 2

    errors = validate_static(root, manifest)
    if not errors and args.mode != "static":
        errors.extend(validate_state(root, manifest, args.mode))
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"ok: branch cleanup manifest {args.mode} validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
