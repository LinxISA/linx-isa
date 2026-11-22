#!/usr/bin/env python3
"""Validate the superproject component topology and exact gitlinks."""

from __future__ import annotations

import argparse
import configparser
import json
import re
import subprocess
from pathlib import Path
from typing import Any


LOCK_PATHS = {
    profile: Path(f"docs/bringup/component-lock.{profile}.json")
    for profile in ("v0.58", "v0.59")
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_COMPONENTS = {
    "compiler/llvm",
    "emulator/qemu",
    "kernel/linux",
    "tools/Linx-TileOP-API",
    "workloads/pto_kernels",
}
EXPECTED_RELEASES = {
    "compiler/llvm": "0.58.7",
    "compiler/ptoas": "0.58.7",
    "emulator/qemu": "0.58.7",
    "kernel/linux": "0.58.3",
    "lib/glibc": "0.58.3",
    "lib/musl": "0.58.3",
    "skills/linx-skills": "0.58.3",
    "tools/Linx-TileOP-API": "0.58.7",
    "tools/model": "0.58.7",
    "workloads/pto_kernels": "0.58.3",
}
FORBIDDEN_COMPONENTS = {"workloads/SuperNPUBench"}
REVIEW_TRACKED_COMPONENTS = {"tools/LinxCoreModel"}
GITHUB_PR_URL_RE = re.compile(r"^https://github\.com/[^/]+/[^/]+/pull/[1-9][0-9]*$")
V059_SYSTEM_COMPONENTS = {"kernel/linux", "lib/glibc", "lib/musl"}
V059_REVIEWED_COMPONENTS = REVIEW_TRACKED_COMPONENTS | V059_SYSTEM_COMPONENTS | {
    "compiler/llvm",
    "emulator/qemu",
    "tools/model",
}


def component_lock_profile(root: Path) -> str:
    return "v0.59" if (root / LOCK_PATHS["v0.59"]).is_file() else "v0.58"


def load_modules(path: Path) -> dict[str, dict[str, str]]:
    parser = configparser.ConfigParser()
    parser.optionxform = str
    with path.open(encoding="utf-8") as stream:
        parser.read_file(stream)
    modules: dict[str, dict[str, str]] = {}
    for section in parser.sections():
        if not section.startswith('submodule "'):
            continue
        values = dict(parser[section])
        component_path = values.get("path", "")
        if component_path:
            modules[component_path] = values
    return modules


def load_gitlinks(root: Path) -> dict[str, str]:
    proc = subprocess.run(
        ["git", "ls-files", "--stage"],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    gitlinks: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        metadata, path = line.split("\t", 1)
        mode, commit, _stage = metadata.split()
        if mode == "160000":
            gitlinks[path] = commit
    return gitlinks


def validate(
    lock: dict[str, Any],
    modules: dict[str, dict[str, str]],
    gitlinks: dict[str, str],
    profile: str = "v0.58",
) -> list[str]:
    errors: list[str] = []
    if lock.get("schema_version") != 1:
        errors.append("component lock schema_version must be 1")
    if lock.get("profile") != profile:
        errors.append(f"component lock profile must be {profile}")

    raw_components = lock.get("components")
    if not isinstance(raw_components, list):
        return [*errors, "component lock components must be a list"]

    locked: dict[str, dict[str, str]] = {}
    for item in raw_components:
        if not isinstance(item, dict):
            errors.append("component lock entries must be objects")
            continue
        path = str(item.get("path", ""))
        if not path:
            errors.append("component lock entry is missing path")
            continue
        if path in locked:
            errors.append(f"duplicate component lock path: {path}")
        locked[path] = {key: str(value) for key, value in item.items()}

    locked_paths = set(locked)
    module_paths = set(modules)
    gitlink_paths = set(gitlinks)
    for forbidden in sorted(FORBIDDEN_COMPONENTS & (locked_paths | module_paths | gitlink_paths)):
        errors.append(f"standalone SuperNPUBench component is forbidden: {forbidden}")
    required = REQUIRED_COMPONENTS
    reviewed = REVIEW_TRACKED_COMPONENTS
    if profile == "v0.59":
        required = required | V059_REVIEWED_COMPONENTS
        reviewed = V059_REVIEWED_COMPONENTS
    missing_required = required - locked_paths
    if missing_required:
        errors.append(f"component lock is missing required {profile} components: {sorted(missing_required)}")
    if locked_paths != module_paths:
        errors.append(
            f"component lock/.gitmodules path mismatch: lock={sorted(locked_paths)} modules={sorted(module_paths)}"
        )
    if locked_paths != gitlink_paths:
        errors.append(
            f"component lock/gitlink path mismatch: lock={sorted(locked_paths)} gitlinks={sorted(gitlink_paths)}"
        )

    for path, item in sorted(locked.items()):
        commit = item.get("commit", "")
        if not SHA_RE.fullmatch(commit):
            errors.append(f"invalid locked commit for {path}: {commit!r}")
        tree = item.get("tree", "")
        if not SHA_RE.fullmatch(tree):
            errors.append(f"invalid locked tree for {path}: {tree!r}")
        if not item.get("role", "").strip():
            errors.append(f"component lock role must be non-empty for {path}")
        expected_release = EXPECTED_RELEASES.get(path)
        if profile == "v0.59" and path in V059_SYSTEM_COMPONENTS:
            expected_release = "0.59.1"
        if expected_release is not None:
            if item.get("release") != expected_release:
                errors.append(
                    f"{path} must record release {expected_release}, "
                    f"got {item.get('release')!r}"
                )
        if path in reviewed:
            integration_status = item.get("integration_status")
            if profile == "v0.59" and integration_status != "merged_development":
                errors.append(f"{path} must record a merged development PR for {profile}")
            elif integration_status not in {"review_only_open_pr", "merged_development"}:
                errors.append(f"{path} must record a review-only open PR or a merged development PR")
            review_url = item.get("review_url", "")
            if not GITHUB_PR_URL_RE.fullmatch(review_url):
                errors.append(f"{path} must record its GitHub review PR URL")
            if integration_status == "review_only_open_pr" and (
                item.get("release_tag", "") or item.get("release_url", "")
            ):
                errors.append(f"{path} review-only pin must not have release metadata")
        module = modules.get(path)
        if module is None:
            continue
        for key in ("url", "branch"):
            expected = item.get(key, "")
            actual = module.get(key, "")
            if actual != expected:
                errors.append(f"{path} {key} mismatch: lock={expected!r} .gitmodules={actual!r}")
        if module.get("update") != "checkout":
            errors.append(f"{path} must use update=checkout")
        actual_commit = gitlinks.get(path)
        if actual_commit is not None and actual_commit != commit:
            errors.append(f"{path} gitlink mismatch: lock={commit} index={actual_commit}")
    return errors


def check_repository(root: Path, profile: str | None = None) -> list[str]:
    profile = profile or component_lock_profile(root)
    lock_path = root / LOCK_PATHS[profile]
    if not lock_path.is_file():
        return [f"component lock is missing: {lock_path}"]
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    return validate(lock, load_modules(root / ".gitmodules"), load_gitlinks(root), profile)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--profile", choices=LOCK_PATHS)
    args = parser.parse_args()
    root = args.root.resolve()
    profile = args.profile or component_lock_profile(root)
    errors = check_repository(root, profile)
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print(f"OK: {profile} component lock matches .gitmodules and gitlinks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
