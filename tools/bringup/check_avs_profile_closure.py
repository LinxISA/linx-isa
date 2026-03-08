#!/usr/bin/env python3
"""Validate AVS closure for a selected gate tier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ALLOWED_VALIDATED = {"pass", "fail", "partial", "not_run"}


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


def _load_status(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    statuses = data.get("statuses")
    if not isinstance(statuses, dict):
        raise SystemExit(f"error: {path} missing object field 'statuses'")
    out: dict[str, dict[str, Any]] = {}
    for test_id, meta in statuses.items():
        if isinstance(meta, dict):
            out[str(test_id)] = meta
    return out


def _must_pass(test: dict[str, Any], *, tier: str) -> bool:
    state = str(test.get("state", "")).strip()
    if state != "active":
        return False
    tiers = test.get("must_pass_in_tier")
    if not isinstance(tiers, list):
        return False
    return tier in {str(item).strip() for item in tiers}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate AVS closure for a selected gate tier")
    ap.add_argument("--matrix", default="avs/linx_avs_v1_test_matrix.yaml")
    ap.add_argument("--status", default="avs/linx_avs_v1_test_matrix_status.json")
    ap.add_argument("--tier", default="pr", choices=["pr", "nightly"])
    ap.add_argument("--report-out", default="", help="Optional JSON report path")
    args = ap.parse_args(argv)

    matrix = _load_yaml_or_json(Path(args.matrix))
    statuses = _load_status(Path(args.status))
    tests = matrix.get("tests")
    if not isinstance(tests, list):
        raise SystemExit(f"error: {args.matrix} missing list field 'tests'")

    required: list[str] = []
    failures: list[str] = []
    for idx, test in enumerate(tests):
        if not isinstance(test, dict):
            failures.append(f"matrix.tests[{idx}] must be an object")
            continue
        test_id = str(test.get("id", "")).strip()
        if not test_id:
            failures.append(f"matrix.tests[{idx}] missing non-empty id")
            continue
        if not _must_pass(test, tier=args.tier):
            continue
        required.append(test_id)
        meta = statuses.get(test_id)
        if meta is None:
            failures.append(f"{test_id}: missing status entry")
            continue
        if meta.get("implemented") is not True:
            failures.append(f"{test_id}: implemented is not true")
        validated = str(meta.get("validated", "not_run"))
        if validated not in ALLOWED_VALIDATED:
            failures.append(f"{test_id}: invalid validated value {validated!r}")
        elif validated != "pass":
            failures.append(f"{test_id}: validated={validated!r} (expected 'pass')")
        evidence = meta.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            failures.append(f"{test_id}: missing non-empty evidence list")

    report = {
        "matrix": str(Path(args.matrix).resolve()),
        "status": str(Path(args.status).resolve()),
        "tier": args.tier,
        "required_tests": required,
        "required_count": len(required),
        "failure_count": len(failures),
        "failures": failures,
        "result": {
            "ok": not failures,
            "classification": "avs_tier_closure_ok" if not failures else "avs_tier_closure_incomplete",
        },
    }

    if args.report_out:
        report_path = Path(args.report_out).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    print(
        "ok: avs tier closure complete "
        f"(tier={args.tier}, required_tests={len(required)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
