#!/usr/bin/env python3
"""
Validate LinxCore performance floor against a baseline contract.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must decode to object")
    return data


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Check LinxCore performance regression floor")
    ap.add_argument("--root", default=".", help="Repository root")
    ap.add_argument(
        "--contract",
        default="docs/bringup/contracts/linxcore_perf_floor.json",
        help="Performance floor contract JSON",
    )
    ap.add_argument(
        "--current",
        default="docs/bringup/gates/linxcore_perf_latest.json",
        help="Current performance measurement JSON",
    )
    ap.add_argument(
        "--max-regression",
        type=float,
        default=None,
        help="Override max regression percent",
    )
    ap.add_argument("--out", default="", help="Optional output JSON report")
    ap.add_argument(
        "--allow-missing-current",
        action="store_true",
        help="Return pass with classification=no_data when current measurement is missing",
    )
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    contract_path = (root / args.contract).resolve()
    current_path = (root / args.current).resolve()

    if not contract_path.is_file():
        print(f"error: missing contract file: {contract_path}", file=sys.stderr)
        return 1

    try:
        contract = _load_json(contract_path)
    except Exception as exc:
        print(f"error: failed to parse contract JSON: {exc}", file=sys.stderr)
        return 1

    metric = str(contract.get("metric", "")).strip()
    baseline = contract.get("baseline", {})
    if not metric:
        print("error: contract.metric must be non-empty", file=sys.stderr)
        return 1
    if not isinstance(baseline, dict):
        print("error: contract.baseline must be object", file=sys.stderr)
        return 1

    try:
        baseline_value = float(baseline.get("value"))
    except Exception:
        print("error: contract.baseline.value must be numeric", file=sys.stderr)
        return 1

    if baseline_value <= 0:
        print("error: contract.baseline.value must be > 0", file=sys.stderr)
        return 1

    max_regression = args.max_regression
    if max_regression is None:
        try:
            max_regression = float(contract.get("max_regression_percent", 10.0))
        except Exception:
            max_regression = 10.0

    report: dict[str, Any] = {
        "ok": False,
        "metric": metric,
        "baseline_value": baseline_value,
        "max_regression_percent": max_regression,
        "classification": "unknown",
    }

    if not current_path.is_file():
        report["classification"] = "no_data"
        report["reason"] = f"missing current measurement: {current_path}"
        if args.allow_missing_current:
            report["ok"] = True
            if args.out:
                out_path = (root / args.out).resolve()
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print("ok: no current performance data (allowed)")
            return 0
        print(f"error: {report['reason']}", file=sys.stderr)
        if args.out:
            out_path = (root / args.out).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 1

    try:
        current = _load_json(current_path)
    except Exception as exc:
        print(f"error: failed to parse current performance JSON: {exc}", file=sys.stderr)
        return 1

    if str(current.get("metric", metric)).strip() != metric:
        print(
            f"error: current metric mismatch: expected {metric!r}, got {current.get('metric')!r}",
            file=sys.stderr,
        )
        return 1

    try:
        current_value = float(current.get("value"))
    except Exception:
        print("error: current.value must be numeric", file=sys.stderr)
        return 1

    if current_value <= 0:
        print("error: current.value must be > 0", file=sys.stderr)
        return 1

    regression_percent = ((baseline_value - current_value) / baseline_value) * 100.0
    report.update(
        {
            "current_value": current_value,
            "regression_percent": regression_percent,
        }
    )

    if regression_percent <= max_regression:
        report["ok"] = True
        report["classification"] = "perf_floor_pass"
    else:
        report["ok"] = False
        report["classification"] = "perf_floor_regression"

    if args.out:
        out_path = (root / args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if not report["ok"]:
        print(
            "error: performance floor failed "
            f"(regression={regression_percent:.2f}% > {max_regression:.2f}%)",
            file=sys.stderr,
        )
        return 1

    print(
        "ok: performance floor passed "
        f"(regression={regression_percent:.2f}% <= {max_regression:.2f}%)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
