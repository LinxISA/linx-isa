#!/usr/bin/env python3
"""
Validate AVS matrix status artifact integrity and emit a summary report.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ID_RE = re.compile(r"^\s*-\s*id:\s*([A-Z0-9-]+)\s*$")
VALIDATED_RE = {"pass", "fail", "not_run", "partial"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _load_matrix_ids(path: Path) -> list[str]:
    ids: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = ID_RE.match(raw)
        if not m:
            continue
        ids.append(m.group(1))
    return ids


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate AVS matrix status JSON against matrix YAML IDs")
    ap.add_argument("--matrix", default="avs/linx_avs_v1_test_matrix.yaml", help="AVS matrix YAML path")
    ap.add_argument(
        "--status",
        default="avs/linx_avs_v1_test_matrix_status.json",
        help="AVS matrix status JSON path",
    )
    ap.add_argument("--report-out", default="", help="Optional JSON summary output path")
    ap.add_argument("--min-implemented", type=int, default=0, help="Fail if implemented count is lower")
    args = ap.parse_args(argv)

    matrix_path = Path(args.matrix).resolve()
    status_path = Path(args.status).resolve()
    if not matrix_path.is_file():
        print(f"error: matrix file not found: {matrix_path}", file=sys.stderr)
        return 1
    if not status_path.is_file():
        print(f"error: status file not found: {status_path}", file=sys.stderr)
        return 1

    matrix_ids = _load_matrix_ids(matrix_path)
    matrix_set = set(matrix_ids)
    if not matrix_set:
        print(f"error: no AVS IDs found in matrix file: {matrix_path}", file=sys.stderr)
        return 1

    status_data = json.loads(status_path.read_text(encoding="utf-8"))
    statuses = status_data.get("statuses")
    if not isinstance(statuses, dict):
        print("error: status JSON missing top-level object 'statuses'", file=sys.stderr)
        return 1

    status_set = set(str(k) for k in statuses.keys())
    missing_status = sorted(matrix_set - status_set)
    extra_status = sorted(status_set - matrix_set)

    implemented = 0
    validated_pass = 0
    validated_unknown: list[str] = []
    for key in matrix_ids:
        item = statuses.get(key)
        if not isinstance(item, dict):
            continue
        if bool(item.get("implemented", False)):
            implemented += 1
        validated = str(item.get("validated", "not_run"))
        if validated == "pass":
            validated_pass += 1
        elif validated not in VALIDATED_RE:
            validated_unknown.append(key)

    if implemented < args.min_implemented:
        print(
            f"error: implemented count {implemented} is lower than --min-implemented {args.min_implemented}",
            file=sys.stderr,
        )
        return 1

    ok = not missing_status and not extra_status and not validated_unknown
    report = {
        "generated_at_utc": _utc_now(),
        "matrix": str(matrix_path),
        "status": str(status_path),
        "matrix_test_count": len(matrix_ids),
        "status_entry_count": len(status_set),
        "implemented_count": implemented,
        "validated_pass_count": validated_pass,
        "missing_status_entries": missing_status,
        "extra_status_entries": extra_status,
        "unknown_validated_entries": validated_unknown,
        "result": {
            "ok": ok,
            "classification": "avs_matrix_status_ok" if ok else "avs_matrix_status_invalid",
        },
    }

    if args.report_out:
        report_path = Path(args.report_out).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if ok:
        print(
            "ok: avs matrix status validated "
            f"(tests={len(matrix_ids)}, implemented={implemented}, pass={validated_pass})"
        )
        return 0

    print(
        "error: avs matrix status mismatch "
        f"(missing={len(missing_status)}, extra={len(extra_status)}, unknown_validated={len(validated_unknown)})",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

