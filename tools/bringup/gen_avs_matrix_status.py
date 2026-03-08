#!/usr/bin/env python3
"""Normalize the canonical AVS status artifact from matrix metadata and evidence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALIDATED_VALUES = {"pass", "fail", "not_run", "partial"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _load_yaml_or_json(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise SystemExit(f"error: expected mapping object in {path}")
    return data


def _normalize_validated(value: Any) -> str:
    validated = str(value or "not_run").strip()
    if validated not in VALIDATED_VALUES:
        return "not_run"
    return validated


def _evidence_kind(repo_root: Path, raw: str) -> tuple[str, str | None, bool | None]:
    text = raw.strip()
    token = text.split()[0].rstrip(",:")
    path = repo_root / token
    if "/" in token and path.exists():
        return "path", token, path.exists()
    return "note", None, None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Generate the canonical AVS matrix status JSON")
    ap.add_argument("--matrix", default="avs/linx_avs_v1_test_matrix.yaml")
    ap.add_argument("--source-status", default="avs/linx_avs_v1_test_matrix_status.json")
    ap.add_argument("--out", default="avs/linx_avs_v1_test_matrix_status.json")
    args = ap.parse_args(argv)

    matrix_path = Path(args.matrix).resolve()
    repo_root = matrix_path.parents[1]
    matrix = _load_yaml_or_json(matrix_path)
    tests = matrix.get("tests")
    if not isinstance(tests, list):
        raise SystemExit("error: matrix.tests must be a list")

    source_path = Path(args.source_status).resolve()
    source_statuses: dict[str, Any] = {}
    if source_path.is_file():
        source_data = json.loads(source_path.read_text(encoding="utf-8"))
        raw_statuses = source_data.get("statuses")
        if isinstance(raw_statuses, dict):
            source_statuses = raw_statuses

    evidence_catalog: dict[str, dict[str, Any]] = {}
    normalized_statuses: dict[str, dict[str, Any]] = {}
    coverage_profile_summaries: dict[str, dict[str, int]] = {}
    tier_summaries: dict[str, dict[str, int]] = {}

    evidence_counter = 0
    for test in tests:
        if not isinstance(test, dict):
            continue
        test_id = str(test.get("id", "")).strip()
        if not test_id:
            continue
        source_meta = source_statuses.get(test_id, {})
        if not isinstance(source_meta, dict):
            source_meta = {}
        implemented = bool(source_meta.get("implemented", False))
        validated = _normalize_validated(source_meta.get("validated"))
        raw_evidence = source_meta.get("evidence")
        evidence_ids: list[str] = []
        if isinstance(raw_evidence, list):
            for raw_item in raw_evidence:
                if not isinstance(raw_item, str) or not raw_item.strip():
                    continue
                evidence_counter += 1
                evidence_id = f"ev-{evidence_counter:04d}"
                kind, rel_path, exists = _evidence_kind(repo_root, raw_item)
                payload: dict[str, Any] = {"kind": kind, "source": raw_item}
                if rel_path is not None:
                    payload["path"] = rel_path
                    payload["exists"] = exists
                evidence_catalog[evidence_id] = payload
                evidence_ids.append(evidence_id)

        normalized_statuses[test_id] = {
            "implemented": implemented,
            "validated": validated,
            "evidence": evidence_ids,
        }

        for profile in test.get("profiles", []):
            if not isinstance(profile, str):
                continue
            slot = coverage_profile_summaries.setdefault(profile, {"tests": 0, "implemented": 0, "pass": 0})
            slot["tests"] += 1
            if implemented:
                slot["implemented"] += 1
            if validated == "pass":
                slot["pass"] += 1

        if str(test.get("state", "")).strip() == "active":
            for tier in test.get("must_pass_in_tier", []):
                if not isinstance(tier, str):
                    continue
                slot = tier_summaries.setdefault(tier, {"tests": 0, "implemented": 0, "pass": 0})
                slot["tests"] += 1
                if implemented:
                    slot["implemented"] += 1
                if validated == "pass":
                    slot["pass"] += 1

    payload = {
        "schema_version": "linx-avs-v0.4-status-v3",
        "generated_at_utc": _utc_now(),
        "matrix_file": str(Path(args.matrix)),
        "coverage_profile_summaries": coverage_profile_summaries,
        "tier_summaries": tier_summaries,
        "evidence_catalog": evidence_catalog,
        "statuses": normalized_statuses,
    }

    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "ok: generated avs matrix status "
        f"(tests={len(normalized_statuses)}, evidence={len(evidence_catalog)}, out={out_path})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
