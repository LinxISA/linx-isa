#!/usr/bin/env python3
"""
Validate the canonical AVS matrix used as the public v0.56 bring-up contract.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL_PROFILES = {
    "LNX-S32",
    "LNX-S64",
    "LNX-PRIV",
    "LNX-ATOM",
    "LNX-FP",
    "LNX-VPAR",
    "LNX-VSEQ",
    "LNX-TILE",
    "LNX-LINUX",
    "LNX-LIBC",
    "LNX-WORKLOAD",
    "LNX-SPEC",
}
ALLOWED_DOMAINS = {"Compiler", "Emulator", "ISA", "Kernel", "Library", "Regression", "Model"}
ALLOWED_STATES = {"active", "archived"}
ALLOWED_TIERS = {"pr", "nightly"}
FORBIDDEN_TOKENS = ("check26", "-draft/")


def _load_yaml_or_json(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except Exception as exc:
            raise SystemExit(f"error: failed to parse {path}: {exc}") from exc
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise SystemExit(f"error: expected mapping object in {path}")
    return data


def _require_string_list(value: Any, *, ctx: str, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise SystemExit(f"error: {ctx} must be a list of strings")
    items = [item.strip() for item in value if item.strip()]
    if not allow_empty and not items:
        raise SystemExit(f"error: {ctx} must be non-empty")
    return items


def _forbidden_text(path: str) -> bool:
    lower = path.lower()
    return any(token in lower for token in FORBIDDEN_TOKENS)


def _validate_spec_ref(repo_root: Path, spec_ref: str, *, ctx: str) -> None:
    if _forbidden_text(spec_ref):
        raise SystemExit(f"error: {ctx} contains forbidden legacy token: {spec_ref}")
    ref_path = repo_root / spec_ref
    if not ref_path.exists():
        raise SystemExit(f"error: {ctx} path does not exist: {spec_ref}")
    if "-draft/" in f"/{spec_ref}":
        raise SystemExit(f"error: {ctx} points at archived draft material: {spec_ref}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate the canonical AVS matrix contract")
    ap.add_argument("--matrix", default="avs/linx_avs_v1_test_matrix.yaml", help="AVS matrix path")
    args = ap.parse_args(argv)

    matrix_path = Path(args.matrix).resolve()
    repo_root = matrix_path.parents[1]
    if not matrix_path.is_file():
        raise SystemExit(f"error: matrix file not found: {matrix_path}")

    data = _load_yaml_or_json(matrix_path)
    version = str(data.get("version", "")).strip()
    if version != "linx-avs-v0.56":
        raise SystemExit(f"error: matrix.version must be 'linx-avs-v0.56' (got {version!r})")
    status = str(data.get("status", "")).strip()
    if status != "canonical":
        raise SystemExit(f"error: matrix.status must be 'canonical' (got {status!r})")
    last_updated = str(data.get("last_updated", "")).strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", last_updated):
        raise SystemExit("error: matrix.last_updated must be YYYY-MM-DD")

    profiles = data.get("profiles")
    if not isinstance(profiles, dict):
        raise SystemExit("error: matrix.profiles must be a mapping")
    missing_profiles = sorted(REQUIRED_TOP_LEVEL_PROFILES - {str(key).strip() for key in profiles})
    if missing_profiles:
        raise SystemExit(f"error: matrix.profiles missing required keys: {missing_profiles}")

    tiers = data.get("tiers")
    if not isinstance(tiers, dict):
        raise SystemExit("error: matrix.tiers must be a mapping")
    missing_tiers = sorted(ALLOWED_TIERS - {str(key).strip() for key in tiers})
    if missing_tiers:
        raise SystemExit(f"error: matrix.tiers missing required keys: {missing_tiers}")

    tests = data.get("tests")
    if not isinstance(tests, list) or not tests:
        raise SystemExit("error: matrix.tests must be a non-empty list")

    seen_ids: set[str] = set()
    for idx, test in enumerate(tests):
        if not isinstance(test, dict):
            raise SystemExit(f"error: matrix.tests[{idx}] must be an object")

        test_id = str(test.get("id", "")).strip()
        if not test_id:
            raise SystemExit(f"error: matrix.tests[{idx}] missing non-empty id")
        if test_id in seen_ids:
            raise SystemExit(f"error: duplicate AVS id: {test_id}")
        seen_ids.add(test_id)

        state = str(test.get("state", "")).strip()
        if state not in ALLOWED_STATES:
            raise SystemExit(f"error: {test_id} invalid state {state!r}")

        area = str(test.get("area", "")).strip()
        if not area:
            raise SystemExit(f"error: {test_id} missing area")

        domain = str(test.get("domain", "")).strip()
        if domain not in ALLOWED_DOMAINS:
            raise SystemExit(f"error: {test_id} invalid domain {domain!r}")

        test_profiles = _require_string_list(test.get("profiles"), ctx=f"{test_id}.profiles")
        unknown_profiles = sorted(set(test_profiles) - set(profiles))
        if unknown_profiles:
            raise SystemExit(f"error: {test_id} uses unknown profiles: {unknown_profiles}")

        if "must_pass_in_profile" in test:
            raise SystemExit(f"error: {test_id} still contains removed field must_pass_in_profile")

        must_pass_tiers = _require_string_list(
            test.get("must_pass_in_tier"),
            ctx=f"{test_id}.must_pass_in_tier",
        )
        unknown_tiers = sorted(set(must_pass_tiers) - ALLOWED_TIERS)
        if unknown_tiers:
            raise SystemExit(f"error: {test_id} uses unknown must_pass_in_tier values: {unknown_tiers}")

        if "check26_ids" in test:
            raise SystemExit(f"error: {test_id} still contains removed field check26_ids")

        requirement = str(test.get("requirement", "")).strip()
        pass_fail = str(test.get("pass_fail", "")).strip()
        if not requirement:
            raise SystemExit(f"error: {test_id} missing requirement")
        if not pass_fail:
            raise SystemExit(f"error: {test_id} missing pass_fail")
        if _forbidden_text(requirement) or _forbidden_text(pass_fail):
            raise SystemExit(f"error: {test_id} requirement/pass_fail contains forbidden legacy wording")

        spec_refs = _require_string_list(test.get("spec_refs"), ctx=f"{test_id}.spec_refs")
        for spec_ref in spec_refs:
            _validate_spec_ref(repo_root, spec_ref, ctx=f"{test_id}.spec_refs")

        if state == "active" and not must_pass_tiers:
            raise SystemExit(f"error: active AVS entry {test_id} must include at least one must_pass_in_tier")

    print(f"ok: avs contract validated (tests={len(tests)}, active={sum(t.get('state') == 'active' for t in tests)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
