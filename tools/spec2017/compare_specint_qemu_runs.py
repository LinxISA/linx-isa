#!/usr/bin/env python3
"""Compare two SPECint QEMU gate summaries row-by-row."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import analyze_specint_qemu_progress as analyzer


DEFAULT_REPORT_OUT = (
    analyzer.REPO_ROOT
    / "workloads"
    / "generated"
    / "specint-qemu-run-compare"
    / "report.json"
)


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _qemu_head(summary: dict[str, Any]) -> str | None:
    provenance = summary.get("qemu_provenance") or {}
    return provenance.get("qemu_repo_head") or provenance.get("repo_head")


def _suite_timeout_by_bench(summary: dict[str, Any]) -> dict[str, float]:
    out: dict[str, float] = {}
    for suite in summary.get("suites") or []:
        if not isinstance(suite, dict):
            continue
        timeout = suite.get("timeout_sec")
        try:
            timeout_float = float(timeout)
        except (TypeError, ValueError):
            continue
        for bench in suite.get("benches") or []:
            out[str(bench)] = timeout_float
    timeout = summary.get("timeout_sec")
    try:
        timeout_float = float(timeout)
    except (TypeError, ValueError):
        return out
    for bench in analyzer.extract_gate_rows(summary, Path(".")).keys():
        out.setdefault(bench, timeout_float)
    return out


def _status(row: dict[str, Any] | None) -> str:
    if not row:
        return "missing"
    if row.get("ok") and row.get("strict_hash_ok"):
        return "pass"
    if row.get("panic_seen"):
        return "panic"
    if row.get("trap_seen"):
        return "trap"
    failure_class = row.get("failure_class")
    if failure_class:
        return str(failure_class)
    if row.get("ok"):
        return "pass"
    return "unknown"


def _is_correctness_bad(status: str) -> bool:
    return status in {"panic", "trap", "user-trap", "kernel-panic"}


def _count_rate(count: int | None, timeout_sec: float | None) -> float | None:
    if count is None or not timeout_sec:
        return None
    return count / timeout_sec


def _to_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value, 0)
        except ValueError:
            return None
    return None


def _pct_delta(base: int | float | None, candidate: int | float | None) -> float | None:
    if base in (None, 0) or candidate is None:
        return None
    return ((candidate - base) / base) * 100.0


def _feature_delta(base: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    base_features = analyzer._features_from_summary(base)
    candidate_features = analyzer._features_from_summary(candidate)
    changes = [
        {
            "feature": key,
            "baseline": base_features[key],
            "candidate": candidate_features[key],
        }
        for key in analyzer.FEATURE_KEYS
        if base_features[key] != candidate_features[key]
    ]
    return {
        "baseline": base_features,
        "candidate": candidate_features,
        "changed": changes,
    }


def _counter_delta(
    base_row: dict[str, Any] | None,
    candidate_row: dict[str, Any] | None,
    key: str,
) -> dict[str, Any]:
    base = _to_int(base_row.get(key)) if base_row else None
    candidate = _to_int(candidate_row.get(key)) if candidate_row else None
    return {
        "baseline": base,
        "candidate": candidate,
        "delta": None if base is None or candidate is None else candidate - base,
        "delta_pct": _pct_delta(base, candidate),
    }


def _verdict(
    base_status: str,
    candidate_status: str,
    count_delta_pct: float | None,
    *,
    threshold_pct: float,
) -> str:
    if base_status == "missing":
        return "new-row"
    if candidate_status == "missing":
        return "missing-row"
    if base_status == "pass" and candidate_status != "pass":
        return "correctness-regressed"
    if base_status != "pass" and candidate_status == "pass":
        return "correctness-improved"
    if not _is_correctness_bad(base_status) and _is_correctness_bad(candidate_status):
        return "correctness-regressed"
    if _is_correctness_bad(base_status) and not _is_correctness_bad(candidate_status):
        return "correctness-improved"
    if count_delta_pct is None:
        return "no-count"
    if count_delta_pct >= threshold_pct:
        return "throughput-improved"
    if count_delta_pct <= -threshold_pct:
        return "throughput-regressed"
    return "throughput-flat"


def build_comparison(
    baseline_summary: dict[str, Any],
    candidate_summary: dict[str, Any],
    baseline_path: Path,
    candidate_path: Path,
    *,
    baseline_label: str = "baseline",
    candidate_label: str = "candidate",
    threshold_pct: float = 2.0,
) -> dict[str, Any]:
    baseline_rows = analyzer.extract_gate_rows(baseline_summary, baseline_path)
    candidate_rows = analyzer.extract_gate_rows(candidate_summary, candidate_path)
    baseline_timeouts = _suite_timeout_by_bench(baseline_summary)
    candidate_timeouts = _suite_timeout_by_bench(candidate_summary)

    rows: list[dict[str, Any]] = []
    for bench in sorted(set(baseline_rows) | set(candidate_rows)):
        base_row = baseline_rows.get(bench)
        cand_row = candidate_rows.get(bench)
        base_count = _to_int(base_row.get("heartbeat_last_count")) if base_row else None
        cand_count = _to_int(cand_row.get("heartbeat_last_count")) if cand_row else None
        base_timeout = baseline_timeouts.get(bench)
        cand_timeout = candidate_timeouts.get(bench)
        base_rate = _count_rate(base_count, base_timeout)
        cand_rate = _count_rate(cand_count, cand_timeout)
        status_base = _status(base_row)
        status_candidate = _status(cand_row)
        delta_pct = _pct_delta(base_count, cand_count)
        rate_delta_pct = _pct_delta(base_rate, cand_rate)
        row = {
            "bench": bench,
            "transport": (cand_row or base_row or {}).get("transport"),
            "baseline_status": status_base,
            "candidate_status": status_candidate,
            "baseline_count": base_count,
            "candidate_count": cand_count,
            "count_delta": None if base_count is None or cand_count is None else cand_count - base_count,
            "count_delta_pct": delta_pct,
            "baseline_timeout_sec": base_timeout,
            "candidate_timeout_sec": cand_timeout,
            "timeout_mismatch": (
                base_timeout is not None
                and cand_timeout is not None
                and base_timeout != cand_timeout
            ),
            "baseline_count_per_sec": base_rate,
            "candidate_count_per_sec": cand_rate,
            "count_per_sec_delta_pct": rate_delta_pct,
            "baseline_bpc": base_row.get("heartbeat_last_bpc") if base_row else None,
            "candidate_bpc": cand_row.get("heartbeat_last_bpc") if cand_row else None,
            "baseline_progress": base_row.get("heartbeat_last_progress") if base_row else None,
            "candidate_progress": cand_row.get("heartbeat_last_progress") if cand_row else None,
            "baseline_failure_class": base_row.get("failure_class") if base_row else None,
            "candidate_failure_class": cand_row.get("failure_class") if cand_row else None,
            "diagnostic_deltas": {
                "tb_lookup": _counter_delta(base_row, cand_row, "tb_lookup"),
                "tb_miss": _counter_delta(base_row, cand_row, "tb_miss"),
                "tlb_fill_total": _counter_delta(base_row, cand_row, "tlb_fill_total"),
                "tlb_fill_user": _counter_delta(base_row, cand_row, "tlb_fill_user"),
                "tlb_inv_iv": _counter_delta(base_row, cand_row, "tlb_inv_iv"),
                "frame_restore_fallback": _counter_delta(base_row, cand_row, "frame_restore_fallback"),
                "frame_single_fast_fentry": _counter_delta(base_row, cand_row, "frame_single_fast_fentry"),
                "frame_page_fast_fentry": _counter_delta(base_row, cand_row, "frame_page_fast_fentry"),
            },
        }
        row["verdict"] = _verdict(
            status_base,
            status_candidate,
            rate_delta_pct if rate_delta_pct is not None else delta_pct,
            threshold_pct=threshold_pct,
        )
        rows.append({key: value for key, value in row.items() if value is not None})

    verdict_counts: dict[str, int] = {}
    for row in rows:
        verdict = str(row["verdict"])
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

    correctness_regressions = verdict_counts.get("correctness-regressed", 0)
    throughput_regressions = verdict_counts.get("throughput-regressed", 0)
    throughput_improvements = verdict_counts.get("throughput-improved", 0)
    timeout_mismatch_benches = [
        row["bench"] for row in rows if row.get("timeout_mismatch")
    ]
    if correctness_regressions:
        recommendation = "reject-candidate-correctness-regression"
    elif throughput_regressions and throughput_improvements:
        recommendation = "mixed-candidate-row-regressions"
    elif throughput_regressions:
        recommendation = "reject-candidate-throughput-regression"
    elif throughput_improvements:
        recommendation = (
            "candidate-improves-measured-rows-timeout-normalized"
            if timeout_mismatch_benches
            else "candidate-improves-measured-rows"
        )
    else:
        recommendation = "candidate-neutral"

    return {
        "schema_version": "linx-specint-qemu-run-compare-v1",
        "generated_at_utc": _utc_now(),
        "threshold_pct": threshold_pct,
        "baseline": {
            "label": baseline_label,
            "summary": str(baseline_path),
            "input_set": baseline_summary.get("profile") or baseline_summary.get("input_set"),
            "qemu": baseline_summary.get("qemu"),
            "qemu_head": _qemu_head(baseline_summary),
            "qemu_provenance": baseline_summary.get("qemu_provenance") or {},
        },
        "candidate": {
            "label": candidate_label,
            "summary": str(candidate_path),
            "input_set": candidate_summary.get("profile") or candidate_summary.get("input_set"),
            "qemu": candidate_summary.get("qemu"),
            "qemu_head": _qemu_head(candidate_summary),
            "qemu_provenance": candidate_summary.get("qemu_provenance") or {},
        },
        "qemu_features": _feature_delta(baseline_summary, candidate_summary),
        "summary": {
            "row_count": len(rows),
            "verdict_counts": verdict_counts,
            "recommendation": recommendation,
            "improved_benches": [
                row["bench"]
                for row in rows
                if row["verdict"] in {"throughput-improved", "correctness-improved"}
            ],
            "regressed_benches": [
                row["bench"]
                for row in rows
                if row["verdict"] in {"throughput-regressed", "correctness-regressed"}
            ],
            "timeout_mismatch_benches": timeout_mismatch_benches,
        },
        "rows": rows,
    }


def _fmt_pct(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:+.2f}%"
    return ""


def _fmt_num(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    if value is None:
        return ""
    return str(value)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    feature_changes = report["qemu_features"].get("changed") or []
    lines = [
        "# SPECint QEMU Run Comparison",
        "",
        f"- generated_at_utc: `{report['generated_at_utc']}`",
        f"- threshold_pct: `{report['threshold_pct']}`",
        f"- baseline: `{report['baseline']['label']}` `{report['baseline']['summary']}`",
        f"- candidate: `{report['candidate']['label']}` `{report['candidate']['summary']}`",
        f"- baseline_qemu_head: `{report['baseline'].get('qemu_head')}`",
        f"- candidate_qemu_head: `{report['candidate'].get('qemu_head')}`",
        f"- recommendation: `{report['summary']['recommendation']}`",
        "",
        "## Feature Changes",
        "",
    ]
    if feature_changes:
        for item in feature_changes:
            lines.append(
                f"- `{item['feature']}`: baseline=`{str(item['baseline']).lower()}`, "
                f"candidate=`{str(item['candidate']).lower()}`"
            )
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Verdicts",
            "",
        ]
    )
    for verdict, count in sorted(report["summary"]["verdict_counts"].items()):
        lines.append(f"- `{verdict}`: {count}")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Bench | Transport | Verdict | Baseline | Candidate | Base timeout | Cand timeout | Count delta | Rate delta | Baseline BPC | Candidate BPC |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in report["rows"]:
        lines.append(
            "| "
            f"`{row['bench']}` | "
            f"`{row.get('transport', '')}` | "
            f"`{row['verdict']}` | "
            f"{_fmt_num(row.get('baseline_count'))} | "
            f"{_fmt_num(row.get('candidate_count'))} | "
            f"{_fmt_num(row.get('baseline_timeout_sec'))} | "
            f"{_fmt_num(row.get('candidate_timeout_sec'))} | "
            f"{_fmt_pct(row.get('count_delta_pct'))} | "
            f"{_fmt_pct(row.get('count_per_sec_delta_pct'))} | "
            f"`{row.get('baseline_bpc', '')}` | "
            f"`{row.get('candidate_bpc', '')}` |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--candidate-label", default="candidate")
    parser.add_argument("--threshold-pct", type=float, default=2.0)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT_OUT)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    baseline_path = Path(os.path.expanduser(str(args.baseline))).resolve()
    candidate_path = Path(os.path.expanduser(str(args.candidate))).resolve()
    report_out = Path(os.path.expanduser(str(args.report_out))).resolve()
    out_md = Path(os.path.expanduser(str(args.out_md))).resolve() if args.out_md else None
    if not baseline_path.is_file():
        raise SystemExit(f"error: missing baseline summary: {baseline_path}")
    if not candidate_path.is_file():
        raise SystemExit(f"error: missing candidate summary: {candidate_path}")

    report = build_comparison(
        _load_json(baseline_path),
        _load_json(candidate_path),
        baseline_path,
        candidate_path,
        baseline_label=args.baseline_label,
        candidate_label=args.candidate_label,
        threshold_pct=args.threshold_pct,
    )
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if out_md:
        out_md.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(out_md, report)
    print(str(report_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
