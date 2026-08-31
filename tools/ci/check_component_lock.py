#!/usr/bin/env python3
"""Validate the exact v0.58 superproject component topology and gitlinks."""

from __future__ import annotations

import argparse
import configparser
import json
import re
import subprocess
from pathlib import Path
from typing import Any


LOCK_PATH = Path("docs/bringup/component-lock.v0.58.json")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_COMPONENTS = {
    "compiler/llvm",
    "emulator/qemu",
    "kernel/linux",
    "tools/Linx-TileOP-API",
    "tools/SuperScalarModel",
    "tools/asl-model",
    "tools/pto-spec",
    "workloads/pto_kernels",
}
RELEASE_0583_COMPONENTS = (REQUIRED_COMPONENTS - {
    "emulator/qemu",
    "tools/SuperScalarModel", "tools/asl-model", "tools/pto-spec"
}) | {
    "compiler/ptoas",
    "emulator/qemu",
    "lib/glibc",
    "lib/musl",
    "skills/linx-skills",
    "tools/model",
}
FORBIDDEN_COMPONENTS = {"workloads/SuperNPUBench"}
GITHUB_PR_URL_RE = re.compile(r"^https://github\.com/[^/]+/[^/]+/pull/[1-9][0-9]*$")


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
    require_merge_ready: bool = False,
) -> list[str]:
    errors: list[str] = []
    if lock.get("schema_version") != 2:
        errors.append("component lock schema_version must be 2")
    if lock.get("profile") != "v0.58":
        errors.append("component lock profile must be v0.58")
    integration_phase = lock.get("integration_phase")
    if integration_phase not in {"draft_staging", "merge_ready"}:
        errors.append("component lock integration_phase must be draft_staging or merge_ready")
    if require_merge_ready and integration_phase != "merge_ready":
        errors.append("component lock is Draft staging evidence, not merge-ready evidence")

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
    missing_required = REQUIRED_COMPONENTS - locked_paths
    if missing_required:
        errors.append(f"component lock is missing required v0.58 components: {sorted(missing_required)}")
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
        if path in RELEASE_0583_COMPONENTS:
            if item.get("release") != "0.58.3":
                errors.append(
                    f"{path} must record release 0.58.3, got {item.get('release')!r}"
                )
        integration_status = item.get("integration_status", "")
        if integration_status:
            if integration_status != "review_only_open_pr":
                errors.append(f"{path} has unsupported integration_status {integration_status!r}")
            review_url = item.get("review_url", "")
            if not GITHUB_PR_URL_RE.fullmatch(review_url):
                errors.append(f"{path} must record its GitHub review PR URL")
            if item.get("release_tag", "") or item.get("release_url", ""):
                errors.append(f"{path} review-only pin must not have release metadata")
            if integration_phase == "merge_ready" or require_merge_ready:
                errors.append(f"{path} open topic head is not merge-ready evidence")
        elif item.get("review_url", ""):
            errors.append(f"{path} review_url requires review_only_open_pr status")
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


def check_repository(root: Path, require_merge_ready: bool = False) -> list[str]:
    lock = json.loads((root / LOCK_PATH).read_text(encoding="utf-8"))
    return validate(
        lock,
        load_modules(root / ".gitmodules"),
        load_gitlinks(root),
        require_merge_ready=require_merge_ready,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--require-merge-ready", action="store_true")
    args = parser.parse_args()
    errors = check_repository(
        args.root.resolve(), require_merge_ready=args.require_merge_ready
    )
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print("OK: v0.58 component lock matches .gitmodules and gitlinks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
