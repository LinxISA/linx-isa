#!/usr/bin/env python3
"""Join SPECint train gate failures with QEMU profile evidence."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

DEFAULT_GATE_SUMMARY = (
    REPO_ROOT
    / "workloads"
    / "generated"
    / "specint-train-all-clean-qemu-20260705-r1"
    / "specint_fast_gate_summary.json"
)
DEFAULT_PROFILE_SUMMARY = (
    REPO_ROOT
    / "workloads"
    / "generated"
    / "specint-profile-suite-train-long-clean-qemu-20260705-r2"
    / "profile_suite_summary.json"
)
DEFAULT_REPORT_OUT = (
    REPO_ROOT
    / "workloads"
    / "generated"
    / "specint-qemu-progress-analysis"
    / "report.json"
)

CROSS_ROW_HOT_SYMBOLS = {
    "linx_template_fentry_impl",
    "linx_template_fret_stk_impl",
    "linx_frame_restore_prepare",
    "linx_frame_restore_commit",
    "tb_lookup",
    "helper_lookup_tb_ptr",
    "mmu_lookup1",
    "probe_access_internal",
    "do_ld8_mmu",
}

TLBI_SYMBOLS = {"helper_linx_tlb_iv"}


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_path(value: str, base_dir: Path) -> Path:
    path = Path(os.path.expanduser(value))
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def _iter_json_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for item in value.values():
            refs.extend(_iter_json_refs(item))
    elif isinstance(value, list):
        for item in value:
            refs.extend(_iter_json_refs(item))
    elif isinstance(value, str) and value.endswith(".json"):
        refs.append(value)
    return refs


def _related_summaries(gate_summary: dict[str, Any], gate_summary_path: Path) -> list[dict[str, Any]]:
    gate_dir = gate_summary_path.parent
    todo = [_as_path(ref, gate_dir) for ref in _iter_json_refs(gate_summary)]
    if gate_dir.exists():
        todo.extend(sorted(gate_dir.rglob("qemu_matrix_summary.json")))
        todo.extend(sorted(gate_dir.rglob("stage_*_summary.json")))

    out: list[dict[str, Any]] = []
    seen: set[Path] = {gate_summary_path.resolve()}
    while todo:
        path = todo.pop(0).resolve()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        try:
            data = _load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        data["_source_path"] = str(path)
        out.append(data)
        for ref in _iter_json_refs(data):
            ref_path = _as_path(ref, path.parent).resolve()
            if ref_path not in seen:
                todo.append(ref_path)
    return out


def _suite_transport(suite: dict[str, Any]) -> str | None:
    transports = suite.get("transports")
    if isinstance(transports, list) and len(transports) == 1:
        return str(transports[0])
    if isinstance(transports, str):
        return transports
    return suite.get("transport")


def _merge_failure_detail(row: dict[str, Any], detail: dict[str, Any]) -> None:
    frame_stats = detail.get("heartbeat_frame_stats") or {}
    frame_shape_hot = detail.get("heartbeat_frame_shape_hot") or {}
    tb_stats = detail.get("heartbeat_tb_stats") or {}
    tlb_fill = detail.get("heartbeat_tlb_fill") or {}
    tlb_inv = detail.get("heartbeat_tlb_invalidation") or {}
    tlb_inv_hot = detail.get("heartbeat_tlb_inv_hot") or {}

    row.update(
        {
            "failure_class": detail.get("failure_class", row.get("failure_class")),
            "heartbeat_running": detail.get("heartbeat_running"),
            "heartbeat_site_progress": detail.get("heartbeat_site_progress"),
            "heartbeat_last_count": detail.get("heartbeat_last_count"),
            "heartbeat_last_bpc": detail.get("heartbeat_last_bpc"),
            "heartbeat_last_progress": detail.get("heartbeat_last_progress"),
            "stalled": detail.get("stalled"),
            "panic_seen": detail.get("panic_seen")
            or detail.get("heartbeat_kernel_panic_loop"),
            "trap_seen": detail.get("trap_seen"),
            "timed_out": detail.get("timed_out"),
            "qemu_log": detail.get("log"),
            "frame_restore_fallback": frame_stats.get("restore_fallback"),
            "frame_restore_host": frame_stats.get("restore_host"),
            "frame_fentry": frame_stats.get("fentry"),
            "frame_fret_stk": frame_stats.get("fret_stk"),
            "frame_shape_hot": frame_shape_hot if frame_shape_hot.get("seen") else {},
            "tb_lookup": tb_stats.get("lookup"),
            "tb_miss": tb_stats.get("miss"),
            "tlb_fill_total": tlb_fill.get("total"),
            "tlb_fill_user": tlb_fill.get("user"),
            "tlb_inv_iv": tlb_inv.get("iv"),
            "tlb_inv_last_pc": tlb_inv.get("last_pc"),
            "tlb_inv_last_bpc": tlb_inv.get("last_bpc"),
            "tlb_inv_hot_max_delta": tlb_inv_hot.get("max_delta"),
            "tlb_inv_hot_max_pc": tlb_inv_hot.get("max_delta_top0_pc"),
            "tlb_inv_hot_max_bpc": tlb_inv_hot.get("max_delta_top0_bpc"),
        }
    )


def _merge_stage_result(row: dict[str, Any], stage_summary: dict[str, Any], bench_row: dict[str, Any]) -> None:
    specdiff = bench_row.get("specdiff") or {}
    hash_checks = specdiff.get("hash_checks") or specdiff.get("checks") or []
    ok_hashes = [item for item in hash_checks if item.get("ok")]
    row.update(
        {
            "ok": bool(bench_row.get("ok")),
            "stage": stage_summary.get("stage", row.get("stage")),
            "input_set": stage_summary.get("input_set", row.get("input_set")),
            "transport": stage_summary.get("transport", row.get("transport")),
            "run_dir": bench_row.get("run_dir", row.get("run_dir")),
            "specdiff_ok": specdiff.get("ok"),
            "strict_hash": specdiff.get("strict_hash"),
            "strict_hash_ok": bool(ok_hashes) and all(item.get("ok") for item in hash_checks),
            "hash_checks": [
                {
                    "output_name": item.get("output_name"),
                    "actual_hash": item.get("actual_hash"),
                    "expected_hash": item.get("expected_hash"),
                    "actual_size": item.get("actual_size"),
                    "expected_size": item.get("expected_size"),
                    "ok": item.get("ok"),
                }
                for item in hash_checks
            ],
        }
    )


def extract_gate_rows(gate_summary: dict[str, Any], gate_summary_path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}

    for suite in gate_summary.get("suites") or []:
        transport = _suite_transport(suite)
        failure_classes = suite.get("failure_classes") or {}
        failure_details = suite.get("failure_details") or {}
        benches = suite.get("benches") or sorted(set(failure_classes) | set(failure_details))
        for bench in benches:
            row = rows.setdefault(bench, {"bench": bench})
            row.update(
                {
                    "gate_suite": suite.get("name"),
                    "stage": suite.get("stage", row.get("stage")),
                    "input_set": suite.get("input_set", row.get("input_set")),
                    "transport": transport or row.get("transport"),
                    "failure_class": failure_classes.get(bench, row.get("failure_class")),
                }
            )
            if bench in failure_details:
                _merge_failure_detail(row, failure_details[bench])

    for summary in _related_summaries(gate_summary, gate_summary_path):
        results = summary.get("results")
        if isinstance(results, dict):
            for bench, bench_row in results.items():
                if not isinstance(bench_row, dict):
                    continue
                row = rows.setdefault(bench, {"bench": bench})
                _merge_stage_result(row, summary, bench_row)
        elif isinstance(results, list):
            for transport_row in results:
                if not isinstance(transport_row, dict):
                    continue
                transport = transport_row.get("transport")
                for bench, failure_class in (transport_row.get("failure_classes") or {}).items():
                    row = rows.setdefault(bench, {"bench": bench})
                    row.update({"transport": transport or row.get("transport"), "failure_class": failure_class})
                for bench, detail in (transport_row.get("failure_details") or {}).items():
                    row = rows.setdefault(bench, {"bench": bench})
                    row["transport"] = transport or row.get("transport")
                    if isinstance(detail, dict):
                        _merge_failure_detail(row, detail)

    return rows


def _profile_by_bench(profile_summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row["bench"]: row
        for row in profile_summary.get("rows") or []
        if isinstance(row, dict) and row.get("bench")
    }


def _top_symbols(profile_row: dict[str, Any] | None) -> set[str]:
    if not profile_row:
        return set()
    return {
        item.get("symbol")
        for item in profile_row.get("top_qemu") or []
        if isinstance(item, dict) and item.get("symbol")
    }


def _dominant_tlbi(profile_row: dict[str, Any] | None) -> bool:
    if not profile_row:
        return False
    top = [
        item
        for item in profile_row.get("top_qemu") or []
        if isinstance(item, dict) and isinstance(item.get("count"), int)
    ]
    if not top:
        return False
    max_count = top[0]["count"]
    for index, item in enumerate(top):
        if item.get("symbol") not in TLBI_SYMBOLS:
            continue
        count = item["count"]
        return index < 3 or count >= 100 or count >= (max_count * 0.5)
    return False


def _top_text(profile_row: dict[str, Any] | None, limit: int = 5) -> str:
    if not profile_row:
        return ""
    items = []
    for item in (profile_row.get("top_qemu") or [])[:limit]:
        symbol = item.get("symbol")
        count = item.get("count")
        if symbol and isinstance(count, int):
            items.append(f"{symbol}={count}")
    return ", ".join(items)


def classify_row(gate_row: dict[str, Any], profile_row: dict[str, Any] | None) -> tuple[str, str]:
    bench = gate_row["bench"]
    symbols = _top_symbols(profile_row)
    transport = gate_row.get("transport")
    failure_class = gate_row.get("failure_class")

    if gate_row.get("ok") and gate_row.get("strict_hash_ok"):
        return (
            "correctness-sentinel-pass",
            "Keep this strict-hash row as the before/after guard for QEMU speed experiments.",
        )
    if gate_row.get("panic_seen") or gate_row.get("trap_seen"):
        return (
            "correctness-debug",
            "Prioritize panic/trap root cause before spending more cycles on throughput.",
        )
    if gate_row.get("stalled") and not gate_row.get("heartbeat_site_progress"):
        return (
            "possible-stall-debug",
            "Use heartbeat same-site diagnostics and symbolization to separate a real stall from slow progress.",
        )
    if failure_class == "live-timeout" and gate_row.get("heartbeat_running"):
        if transport == "9p":
            return (
                "transport-9p-throughput",
                "Profile 9p/kernel transport separately; do not mix this row with initramfs throughput decisions.",
            )
        if _dominant_tlbi(profile_row):
            return (
                "linux-tlbi-attribution",
                "Attribute and reduce Linux TLBI/fixmap churn before changing broad QEMU cputlb behavior.",
            )
        if symbols & CROSS_ROW_HOT_SYMBOLS:
            return (
                "template-tb-mmu-throughput",
                "Target template entry/return, TB lookup/dispatch, and soft-MMU probe/load lookup in QEMU.",
            )
        return (
            "live-throughput-unattributed",
            "Collect a delayed post-marker QEMU profile before selecting an optimization lane.",
        )
    if bench == "999.specrand_ir" and gate_row.get("ok"):
        return (
            "sentinel-pass",
            "Preserve this row as the cheap correctness smoke even when strict hash metadata is absent.",
        )
    return (
        "unclassified",
        "Inspect row logs and add a more specific failure classifier before changing QEMU.",
    )


def _bench_report_row(
    gate_row: dict[str, Any],
    profile_row: dict[str, Any] | None,
) -> dict[str, Any]:
    lane, action = classify_row(gate_row, profile_row)
    out = {
        "bench": gate_row["bench"],
        "transport": gate_row.get("transport"),
        "gate_ok": gate_row.get("ok"),
        "failure_class": gate_row.get("failure_class"),
        "heartbeat_running": gate_row.get("heartbeat_running"),
        "heartbeat_site_progress": gate_row.get("heartbeat_site_progress"),
        "stalled": gate_row.get("stalled"),
        "panic_seen": gate_row.get("panic_seen"),
        "trap_seen": gate_row.get("trap_seen"),
        "heartbeat_last_count": gate_row.get("heartbeat_last_count"),
        "heartbeat_last_bpc": gate_row.get("heartbeat_last_bpc"),
        "tb_lookup": gate_row.get("tb_lookup"),
        "tb_miss": gate_row.get("tb_miss"),
        "tlb_fill_total": gate_row.get("tlb_fill_total"),
        "tlb_fill_user": gate_row.get("tlb_fill_user"),
        "tlb_inv_iv": gate_row.get("tlb_inv_iv"),
        "frame_restore_fallback": gate_row.get("frame_restore_fallback"),
        "frame_shape_hot": gate_row.get("frame_shape_hot") or {},
        "strict_hash_ok": gate_row.get("strict_hash_ok"),
        "hash_checks": gate_row.get("hash_checks", []),
        "profile_sample_ok": bool(profile_row and profile_row.get("sample_ok")),
        "profile_transport": profile_row.get("transport") if profile_row else None,
        "top_qemu": profile_row.get("top_qemu", []) if profile_row else [],
        "lane": lane,
        "proposed_action": action,
    }
    return {key: value for key, value in out.items() if value is not None}


def _lane_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lanes: dict[str, dict[str, Any]] = {}
    for row in rows:
        lane = row["lane"]
        slot = lanes.setdefault(lane, {"lane": lane, "benches": [], "top_qemu_symbols": {}})
        slot["benches"].append(row["bench"])
        for item in row.get("top_qemu") or []:
            symbol = item.get("symbol")
            count = item.get("count")
            if not symbol or not isinstance(count, int):
                continue
            slot["top_qemu_symbols"][symbol] = slot["top_qemu_symbols"].get(symbol, 0) + count

    out: list[dict[str, Any]] = []
    for lane, slot in sorted(lanes.items()):
        symbols = [
            {"symbol": symbol, "count": count}
            for symbol, count in sorted(
                slot["top_qemu_symbols"].items(),
                key=lambda item: (-item[1], item[0]),
            )[:8]
        ]
        out.append(
            {
                "lane": lane,
                "bench_count": len(slot["benches"]),
                "benches": slot["benches"],
                "top_qemu_symbols": symbols,
            }
        )
    return out


def build_analysis(
    gate_summary: dict[str, Any],
    profile_summary: dict[str, Any],
    gate_summary_path: Path,
    profile_summary_path: Path,
) -> dict[str, Any]:
    gate_rows = extract_gate_rows(gate_summary, gate_summary_path)
    profile_rows = _profile_by_bench(profile_summary)

    rows = [
        _bench_report_row(gate_row, profile_rows.get(bench))
        for bench, gate_row in sorted(gate_rows.items())
    ]
    passing = [row["bench"] for row in rows if row.get("gate_ok")]
    failing = [row["bench"] for row in rows if not row.get("gate_ok")]

    return {
        "schema_version": "linx-specint-qemu-progress-analysis-v1",
        "generated_at_utc": _utc_now(),
        "gate_summary": str(gate_summary_path),
        "profile_summary": str(profile_summary_path),
        "input_set": gate_summary.get("profile") or profile_summary.get("input_set"),
        "stage": profile_summary.get("stage"),
        "qemu": {
            "gate": gate_summary.get("qemu"),
            "profile": profile_summary.get("qemu"),
            "gate_provenance": gate_summary.get("qemu_provenance") or {},
            "profile_provenance": profile_summary.get("qemu_provenance") or {},
        },
        "completion_status": {
            "spec_train_correctness_complete": not failing,
            "passing_benches": passing,
            "failing_benches": failing,
            "reason": (
                "All gate rows passed."
                if not failing
                else "Only the strict sentinel is passing; remaining rows are live-throughput failures."
            ),
        },
        "benchmarks": rows,
        "lanes": _lane_summary(rows),
        "aggregate_top_qemu": profile_summary.get("aggregate_top_qemu") or [],
    }


def _write_markdown(path: Path, report: dict[str, Any]) -> None:
    qemu = report["qemu"]
    gate_head = qemu.get("gate_provenance", {}).get("qemu_repo_head")
    profile_head = qemu.get("profile_provenance", {}).get("qemu_repo_head")
    lines = [
        "# SPECint QEMU Progress Analysis",
        "",
        f"- generated_at_utc: `{report['generated_at_utc']}`",
        f"- input_set: `{report.get('input_set')}`",
        f"- gate_summary: `{report['gate_summary']}`",
        f"- profile_summary: `{report['profile_summary']}`",
        f"- gate_qemu_head: `{gate_head}`",
        f"- profile_qemu_head: `{profile_head}`",
        "",
        "## Completion",
        "",
        f"- spec_train_correctness_complete: `{str(report['completion_status']['spec_train_correctness_complete']).lower()}`",
        f"- passing_benches: `{', '.join(report['completion_status']['passing_benches'])}`",
        f"- failing_benches: `{', '.join(report['completion_status']['failing_benches'])}`",
        "",
        "## Rows",
        "",
        "| Bench | Transport | Gate | Count | BPC | Profile | Lane | Top QEMU frames | Next action |",
        "| --- | --- | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in report["benchmarks"]:
        gate = "pass" if row.get("gate_ok") else row.get("failure_class", "fail")
        top = _top_text(row, 5)
        lines.append(
            "| "
            f"`{row['bench']}` | "
            f"`{row.get('transport', '')}` | "
            f"`{gate}` | "
            f"{row.get('heartbeat_last_count', '')} | "
            f"`{row.get('heartbeat_last_bpc', '')}` | "
            f"`{str(row.get('profile_sample_ok', False)).lower()}` | "
            f"`{row['lane']}` | "
            f"`{top}` | "
            f"{row['proposed_action']} |"
        )

    lines.extend(["", "## Lanes", ""])
    for lane in report["lanes"]:
        top = ", ".join(
            f"{item['symbol']}={item['count']}"
            for item in lane.get("top_qemu_symbols") or []
        )
        lines.append(
            f"- `{lane['lane']}`: {lane['bench_count']} row(s): "
            f"`{', '.join(lane['benches'])}`"
        )
        if top:
            lines.append(f"  Top QEMU symbols: `{top}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate-summary", type=Path, default=DEFAULT_GATE_SUMMARY)
    parser.add_argument("--profile-summary", type=Path, default=DEFAULT_PROFILE_SUMMARY)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT_OUT)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    gate_summary_path = Path(os.path.expanduser(str(args.gate_summary))).resolve()
    profile_summary_path = Path(os.path.expanduser(str(args.profile_summary))).resolve()
    report_out = Path(os.path.expanduser(str(args.report_out))).resolve()
    out_md = Path(os.path.expanduser(str(args.out_md))).resolve() if args.out_md else None

    if not gate_summary_path.is_file():
        raise SystemExit(f"error: missing gate summary: {gate_summary_path}")
    if not profile_summary_path.is_file():
        raise SystemExit(f"error: missing profile summary: {profile_summary_path}")

    report = build_analysis(
        _load_json(gate_summary_path),
        _load_json(profile_summary_path),
        gate_summary_path,
        profile_summary_path,
    )
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if out_md:
        out_md.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(out_md, report)
    print(str(report_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
