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

PROFILE_WRAPPER_SYMBOLS = {
    "cpu_exec",
    "cpu_exec_setjmp",
    "cpu_exec_loop",
    "cpu_loop_exec_tb",
}

FEATURE_KEYS = (
    "template_chain",
    "qemu_frame_stats",
    "qemu_frame_shape_hot",
    "qemu_frame_single_reg_fast",
    "qemu_frame_page_fast",
    "qemu_frame_restore_host_load",
    "qemu_mmu_cache",
    "qemu_mmu_cache_stats",
    "qemu_mmu_cache_assoc2",
    "qemu_mmu_cache_victim",
    "qemu_tb_stats",
    "qemu_tlb_stats",
    "qemu_tlb_inv_hot",
    "qemu_tlb_fill_stats",
    "qemu_tlb_fill_hot",
)

FEATURE_FLAGS = {
    "template_chain": "--template-chain",
    "qemu_frame_stats": "--qemu-frame-stats",
    "qemu_frame_shape_hot": "--qemu-frame-shape-hot",
    "qemu_frame_single_reg_fast": "--qemu-frame-single-reg-fast",
    "qemu_frame_page_fast": "--qemu-frame-page-fast",
    "qemu_frame_restore_host_load": "--qemu-frame-restore-host-load",
    "qemu_mmu_cache": "--qemu-mmu-cache",
    "qemu_mmu_cache_stats": "--qemu-mmu-cache-stats",
    "qemu_mmu_cache_assoc2": "--qemu-mmu-cache-assoc2",
    "qemu_mmu_cache_victim": "--qemu-mmu-cache-victim",
    "qemu_tb_stats": "--qemu-tb-stats",
    "qemu_tlb_stats": "--qemu-tlb-stats",
    "qemu_tlb_inv_hot": "--qemu-tlb-inv-hot",
    "qemu_tlb_fill_stats": "--qemu-tlb-fill-stats",
    "qemu_tlb_fill_hot": "--qemu-tlb-fill-hot",
}

FEATURE_ENVS = {
    "template_chain": "LINX_QEMU_TEMPLATE_CHAIN",
    "qemu_frame_stats": "LINX_QEMU_FRAME_STATS",
    "qemu_frame_shape_hot": "LINX_QEMU_FRAME_SHAPE_HOT",
    "qemu_frame_single_reg_fast": "LINX_QEMU_FRAME_SINGLE_REG_FAST",
    "qemu_frame_page_fast": "LINX_QEMU_FRAME_PAGE_FAST",
    "qemu_frame_restore_host_load": "LINX_QEMU_FRAME_RESTORE_HOST_LOAD",
    "qemu_mmu_cache": "LINX_QEMU_MMU_CACHE",
    "qemu_mmu_cache_stats": "LINX_QEMU_MMU_CACHE_STATS",
    "qemu_mmu_cache_assoc2": "LINX_QEMU_MMU_CACHE_ASSOC2",
    "qemu_mmu_cache_victim": "LINX_QEMU_MMU_CACHE_VICTIM",
    "qemu_tb_stats": "LINX_QEMU_TB_STATS",
    "qemu_tlb_stats": "LINX_QEMU_TLB_STATS",
    "qemu_tlb_inv_hot": "LINX_QEMU_TLB_INV_HOT",
    "qemu_tlb_fill_stats": "LINX_QEMU_TLB_FILL_STATS",
    "qemu_tlb_fill_hot": "LINX_QEMU_TLB_FILL_HOT",
}


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
    child_maps = detail.get("child_maps") or {}
    pc_watch = detail.get("pc_watch") or {}

    row.update(
        {
            "failure_class": detail.get("failure_class", row.get("failure_class")),
            "failure_evidence": detail.get("failure_evidence", row.get("failure_evidence")),
            "heartbeat_running": detail.get("heartbeat_running"),
            "heartbeat_site_progress": detail.get("heartbeat_site_progress"),
            "heartbeat_last_count": detail.get("heartbeat_last_count"),
            "heartbeat_last_bpc": detail.get("heartbeat_last_bpc"),
            "heartbeat_last_progress": detail.get("heartbeat_last_progress"),
            "heartbeat_last_same_site": detail.get("heartbeat_last_same_site"),
            "heartbeat_recent_unique_sites": detail.get("heartbeat_recent_unique_sites"),
            "heartbeat_recent_count_delta": detail.get("heartbeat_recent_count_delta"),
            "heartbeat_recent_sites": detail.get("heartbeat_recent_sites", []),
            "stalled": detail.get("stalled"),
            "panic_seen": detail.get("panic_seen")
            or detail.get("heartbeat_kernel_panic_loop"),
            "trap_seen": detail.get("trap_seen"),
            "timed_out": detail.get("timed_out"),
            "qemu_log": detail.get("log"),
            "qemu_debug_env": detail.get("qemu_debug_env", row.get("qemu_debug_env", {})),
            "fault_trace_seen": detail.get("fault_trace_seen"),
            "fault_trace_count": detail.get("fault_trace_count"),
            "fault_trace_last": detail.get("fault_trace_last"),
            "fault_trace_samples": detail.get("fault_trace_samples", []),
            "mem_trace_seen": detail.get("mem_trace_seen"),
            "mem_trace_count": detail.get("mem_trace_count"),
            "mem_trace_last": detail.get("mem_trace_last"),
            "mem_trace_samples": detail.get("mem_trace_samples", []),
            "syscall_trace_seen": detail.get("syscall_trace_seen"),
            "syscall_trace_count": detail.get("syscall_trace_count"),
            "syscall_trace_last": detail.get("syscall_trace_last"),
            "syscall_trace_samples": detail.get("syscall_trace_samples", []),
            "fentry_trace_seen": detail.get("fentry_trace_seen"),
            "fentry_trace_count": detail.get("fentry_trace_count"),
            "fentry_trace_last": detail.get("fentry_trace_last"),
            "fentry_trace_samples": detail.get("fentry_trace_samples", []),
            "fret_stk_trace_seen": detail.get("fret_stk_trace_seen"),
            "fret_stk_trace_count": detail.get("fret_stk_trace_count"),
            "fret_stk_trace_last": detail.get("fret_stk_trace_last"),
            "fret_stk_trace_samples": detail.get("fret_stk_trace_samples", []),
            "acre_trace_seen": detail.get("acre_trace_seen"),
            "acre_trace_count": detail.get("acre_trace_count"),
            "acre_trace_last": detail.get("acre_trace_last"),
            "acre_trace_samples": detail.get("acre_trace_samples", []),
            "queue_trace_seen": detail.get("queue_trace_seen"),
            "queue_trace_count": detail.get("queue_trace_count"),
            "queue_trace_last": detail.get("queue_trace_last"),
            "queue_trace_samples": detail.get("queue_trace_samples", []),
            "pc_watch_seen": detail.get("pc_watch_seen", pc_watch.get("seen")),
            "pc_watch_line_count": detail.get(
                "pc_watch_line_count", pc_watch.get("line_count")
            ),
            "pc_watch_last": detail.get("pc_watch_last", pc_watch.get("last")),
            "pc_watch_samples": detail.get(
                "pc_watch_samples", pc_watch.get("samples", [])
            ),
            "pc_watch_ring_seen": detail.get(
                "pc_watch_ring_seen", pc_watch.get("ring_seen")
            ),
            "pc_watch_ring_count": detail.get(
                "pc_watch_ring_count", pc_watch.get("ring_count")
            ),
            "pc_watch_ring_entry_count": detail.get(
                "pc_watch_ring_entry_count", pc_watch.get("ring_entry_count")
            ),
            "pc_watch_last_ring": detail.get(
                "pc_watch_last_ring", pc_watch.get("last_ring")
            ),
            "pc_watch_last_ring_entry": detail.get(
                "pc_watch_last_ring_entry", pc_watch.get("last_ring_entry")
            ),
            "pc_watch_last_ring_fields": detail.get(
                "pc_watch_last_ring_fields", pc_watch.get("last_ring_fields", {})
            ),
            "pc_watch_last_ring_entry_fields": detail.get(
                "pc_watch_last_ring_entry_fields",
                pc_watch.get("last_ring_entry_fields", {}),
            ),
            "pc_watch_ring_entry_samples": detail.get(
                "pc_watch_ring_entry_samples",
                pc_watch.get("ring_entry_samples", []),
            ),
            "pc_watch_call_trace_ring_seen": detail.get(
                "pc_watch_call_trace_ring_seen",
                pc_watch.get("call_trace_ring_seen"),
            ),
            "pc_watch_call_trace_ring_count": detail.get(
                "pc_watch_call_trace_ring_count",
                pc_watch.get("call_trace_ring_count"),
            ),
            "pc_watch_call_trace_ring_entry_count": detail.get(
                "pc_watch_call_trace_ring_entry_count",
                pc_watch.get("call_trace_ring_entry_count"),
            ),
            "pc_watch_last_call_trace_ring": detail.get(
                "pc_watch_last_call_trace_ring",
                pc_watch.get("last_call_trace_ring"),
            ),
            "pc_watch_last_call_trace_ring_entry": detail.get(
                "pc_watch_last_call_trace_ring_entry",
                pc_watch.get("last_call_trace_ring_entry"),
            ),
            "pc_watch_last_call_trace_ring_fields": detail.get(
                "pc_watch_last_call_trace_ring_fields",
                pc_watch.get("last_call_trace_ring_fields", {}),
            ),
            "pc_watch_last_call_trace_ring_entry_fields": detail.get(
                "pc_watch_last_call_trace_ring_entry_fields",
                pc_watch.get("last_call_trace_ring_entry_fields", {}),
            ),
            "pc_watch_call_trace_ring_entry_samples": detail.get(
                "pc_watch_call_trace_ring_entry_samples",
                pc_watch.get("call_trace_ring_entry_samples", []),
            ),
            "child_maps_seen": child_maps.get("seen"),
            "child_maps_block_count": child_maps.get("block_count"),
            "child_maps_trap_addr": child_maps.get("trap_addr"),
            "child_maps_trap_addr_mapped": child_maps.get("trap_addr_mapped"),
            "child_maps_trap_addr_line": child_maps.get("trap_addr_line"),
            "child_maps_fault_addr": child_maps.get("fault_addr"),
            "child_maps_fault_addr_mapped": child_maps.get("fault_addr_mapped"),
            "child_maps_fault_addr_line": child_maps.get("fault_addr_line"),
            "mprotect_trace_seen": detail.get("mprotect_trace_seen"),
            "mprotect_trace_count": detail.get("mprotect_trace_count"),
            "mprotect_trace_last": detail.get("mprotect_trace_last"),
            "mprotect_trace_samples": detail.get("mprotect_trace_samples", []),
            "pc_watch_seen": pc_watch.get("seen"),
            "pc_watch_last": pc_watch.get("last"),
            "pc_watch_samples": pc_watch.get("samples", []),
            "frame_restore_fallback": frame_stats.get("restore_fallback"),
            "frame_restore_host": frame_stats.get("restore_host"),
            "frame_fentry": frame_stats.get("fentry"),
            "frame_fret_stk": frame_stats.get("fret_stk"),
            "frame_single_fast_fentry": frame_stats.get("single_fast_fentry"),
            "frame_single_fast_fret_stk": frame_stats.get("single_fast_fret_stk"),
            "frame_page_fast_fentry": frame_stats.get("page_fast_fentry"),
            "frame_page_fast_restore": frame_stats.get("page_fast_restore"),
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
            "tlb_inv_hot_kernel_symbolized": detail.get("tlb_inv_hot_kernel_symbolized"),
            "tlb_inv_hot_kernel_symbol_evidence": detail.get("tlb_inv_hot_kernel_symbol_evidence"),
            "tlb_inv_hot_kernel_symbols": detail.get("tlb_inv_hot_kernel_symbols", []),
        }
    )


def _qemu_run_detail(bench_row: dict[str, Any]) -> dict[str, Any] | None:
    qemu_rows = bench_row.get("qemu")
    if not isinstance(qemu_rows, list):
        return None
    candidates = [item for item in qemu_rows if isinstance(item, dict)]
    if not candidates:
        return None
    for item in candidates:
        if item.get("failure_class") not in (None, "", "none") or item.get("trap_seen"):
            return item
    return candidates[0]


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
    qemu_detail = _qemu_run_detail(bench_row)
    if qemu_detail:
        _merge_failure_detail(row, qemu_detail)


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

    summaries = [gate_summary]
    summaries.extend(_related_summaries(gate_summary, gate_summary_path))
    for summary in summaries:
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


def _is_profile_wrapper_symbol(symbol: str | None) -> bool:
    return bool(symbol and symbol in PROFILE_WRAPPER_SYMBOLS)


def _profile_top_frames(
    profile_row: dict[str, Any] | None,
    *,
    wrappers: bool = False,
) -> list[dict[str, Any]]:
    if not profile_row:
        return []
    out = []
    for item in profile_row.get("top_qemu") or []:
        if not isinstance(item, dict):
            continue
        symbol = item.get("symbol")
        count = item.get("count")
        if not symbol or not isinstance(count, int):
            continue
        if _is_profile_wrapper_symbol(symbol) != wrappers:
            continue
        out.append({"symbol": symbol, "count": count})
    return out


def _actionable_profile_row(profile_row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not profile_row:
        return None
    out = dict(profile_row)
    out["top_qemu"] = _profile_top_frames(profile_row)
    return out


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
    actionable_profile = _actionable_profile_row(profile_row)
    symbols = _top_symbols(actionable_profile)
    transport = gate_row.get("transport")
    failure_class = gate_row.get("failure_class")

    if gate_row.get("ok") and gate_row.get("strict_hash_ok"):
        return (
            "correctness-sentinel-pass",
            "Keep this strict-hash row as the before/after guard for QEMU speed experiments.",
        )
    if gate_row.get("panic_seen") or gate_row.get("trap_seen"):
        if gate_row.get("fault_trace_seen"):
            return (
                "correctness-fault-trace-debug",
                "Correlate the fatal trap with the recent LINX_FAULT_TRACE records before changing throughput paths.",
            )
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
        if _dominant_tlbi(actionable_profile):
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
    raw_top_qemu = profile_row.get("top_qemu", []) if profile_row else []
    actionable_top_qemu = _profile_top_frames(profile_row)
    wrapper_top_qemu = _profile_top_frames(profile_row, wrappers=True)
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
        "failure_evidence": gate_row.get("failure_evidence"),
        "heartbeat_last_count": gate_row.get("heartbeat_last_count"),
        "heartbeat_last_bpc": gate_row.get("heartbeat_last_bpc"),
        "heartbeat_last_progress": gate_row.get("heartbeat_last_progress"),
        "heartbeat_recent_unique_sites": gate_row.get("heartbeat_recent_unique_sites"),
        "heartbeat_recent_count_delta": gate_row.get("heartbeat_recent_count_delta"),
        "heartbeat_recent_sites": gate_row.get("heartbeat_recent_sites", []),
        "qemu_debug_env": gate_row.get("qemu_debug_env", {}),
        "fault_trace_seen": gate_row.get("fault_trace_seen"),
        "fault_trace_count": gate_row.get("fault_trace_count"),
        "fault_trace_last": gate_row.get("fault_trace_last"),
        "fault_trace_samples": gate_row.get("fault_trace_samples", []),
        "mem_trace_seen": gate_row.get("mem_trace_seen"),
        "mem_trace_count": gate_row.get("mem_trace_count"),
        "mem_trace_last": gate_row.get("mem_trace_last"),
        "mem_trace_samples": gate_row.get("mem_trace_samples", []),
        "syscall_trace_seen": gate_row.get("syscall_trace_seen"),
        "syscall_trace_count": gate_row.get("syscall_trace_count"),
        "syscall_trace_last": gate_row.get("syscall_trace_last"),
        "syscall_trace_samples": gate_row.get("syscall_trace_samples", []),
        "fentry_trace_seen": gate_row.get("fentry_trace_seen"),
        "fentry_trace_count": gate_row.get("fentry_trace_count"),
        "fentry_trace_last": gate_row.get("fentry_trace_last"),
        "fentry_trace_samples": gate_row.get("fentry_trace_samples", []),
        "fret_stk_trace_seen": gate_row.get("fret_stk_trace_seen"),
        "fret_stk_trace_count": gate_row.get("fret_stk_trace_count"),
        "fret_stk_trace_last": gate_row.get("fret_stk_trace_last"),
        "fret_stk_trace_samples": gate_row.get("fret_stk_trace_samples", []),
        "acre_trace_seen": gate_row.get("acre_trace_seen"),
        "acre_trace_count": gate_row.get("acre_trace_count"),
        "acre_trace_last": gate_row.get("acre_trace_last"),
        "acre_trace_samples": gate_row.get("acre_trace_samples", []),
        "queue_trace_seen": gate_row.get("queue_trace_seen"),
        "queue_trace_count": gate_row.get("queue_trace_count"),
        "queue_trace_last": gate_row.get("queue_trace_last"),
        "queue_trace_samples": gate_row.get("queue_trace_samples", []),
        "child_maps_seen": gate_row.get("child_maps_seen"),
        "child_maps_block_count": gate_row.get("child_maps_block_count"),
        "child_maps_trap_addr": gate_row.get("child_maps_trap_addr"),
        "child_maps_trap_addr_mapped": gate_row.get("child_maps_trap_addr_mapped"),
        "child_maps_trap_addr_line": gate_row.get("child_maps_trap_addr_line"),
        "child_maps_fault_addr": gate_row.get("child_maps_fault_addr"),
        "child_maps_fault_addr_mapped": gate_row.get("child_maps_fault_addr_mapped"),
        "child_maps_fault_addr_line": gate_row.get("child_maps_fault_addr_line"),
        "mprotect_trace_seen": gate_row.get("mprotect_trace_seen"),
        "mprotect_trace_count": gate_row.get("mprotect_trace_count"),
        "pc_watch_seen": gate_row.get("pc_watch_seen"),
        "pc_watch_line_count": gate_row.get("pc_watch_line_count"),
        "pc_watch_last": gate_row.get("pc_watch_last"),
        "pc_watch_samples": gate_row.get("pc_watch_samples", []),
        "pc_watch_ring_seen": gate_row.get("pc_watch_ring_seen"),
        "pc_watch_ring_count": gate_row.get("pc_watch_ring_count"),
        "pc_watch_ring_entry_count": gate_row.get("pc_watch_ring_entry_count"),
        "pc_watch_last_ring": gate_row.get("pc_watch_last_ring"),
        "pc_watch_last_ring_entry": gate_row.get("pc_watch_last_ring_entry"),
        "pc_watch_last_ring_fields": gate_row.get("pc_watch_last_ring_fields", {}),
        "pc_watch_last_ring_entry_fields": gate_row.get(
            "pc_watch_last_ring_entry_fields", {}
        ),
        "pc_watch_ring_entry_samples": gate_row.get("pc_watch_ring_entry_samples", []),
        "pc_watch_call_trace_ring_seen": gate_row.get("pc_watch_call_trace_ring_seen"),
        "pc_watch_call_trace_ring_count": gate_row.get("pc_watch_call_trace_ring_count"),
        "pc_watch_call_trace_ring_entry_count": gate_row.get(
            "pc_watch_call_trace_ring_entry_count"
        ),
        "pc_watch_last_call_trace_ring": gate_row.get("pc_watch_last_call_trace_ring"),
        "pc_watch_last_call_trace_ring_entry": gate_row.get(
            "pc_watch_last_call_trace_ring_entry"
        ),
        "pc_watch_last_call_trace_ring_fields": gate_row.get(
            "pc_watch_last_call_trace_ring_fields", {}
        ),
        "pc_watch_last_call_trace_ring_entry_fields": gate_row.get(
            "pc_watch_last_call_trace_ring_entry_fields", {}
        ),
        "pc_watch_call_trace_ring_entry_samples": gate_row.get(
            "pc_watch_call_trace_ring_entry_samples", []
        ),
        "tb_lookup": gate_row.get("tb_lookup"),
        "tb_miss": gate_row.get("tb_miss"),
        "tlb_fill_total": gate_row.get("tlb_fill_total"),
        "tlb_fill_user": gate_row.get("tlb_fill_user"),
        "tlb_inv_iv": gate_row.get("tlb_inv_iv"),
        "tlb_inv_hot_max_delta": gate_row.get("tlb_inv_hot_max_delta"),
        "tlb_inv_hot_max_pc": gate_row.get("tlb_inv_hot_max_pc"),
        "tlb_inv_hot_max_bpc": gate_row.get("tlb_inv_hot_max_bpc"),
        "tlb_inv_hot_kernel_symbolized": gate_row.get("tlb_inv_hot_kernel_symbolized"),
        "tlb_inv_hot_kernel_symbol_evidence": gate_row.get("tlb_inv_hot_kernel_symbol_evidence"),
        "tlb_inv_hot_kernel_symbols": gate_row.get("tlb_inv_hot_kernel_symbols", []),
        "frame_restore_fallback": gate_row.get("frame_restore_fallback"),
        "frame_single_fast_fentry": gate_row.get("frame_single_fast_fentry"),
        "frame_single_fast_fret_stk": gate_row.get("frame_single_fast_fret_stk"),
        "frame_page_fast_fentry": gate_row.get("frame_page_fast_fentry"),
        "frame_page_fast_restore": gate_row.get("frame_page_fast_restore"),
        "frame_shape_hot": gate_row.get("frame_shape_hot") or {},
        "strict_hash_ok": gate_row.get("strict_hash_ok"),
        "hash_checks": gate_row.get("hash_checks", []),
        "profile_sample_ok": bool(profile_row and profile_row.get("sample_ok")),
        "profile_transport": profile_row.get("transport") if profile_row else None,
        "top_qemu": actionable_top_qemu,
        "raw_top_qemu": raw_top_qemu,
        "profile_wrapper_qemu": wrapper_top_qemu,
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


def _features_from_summary(summary: dict[str, Any]) -> dict[str, bool]:
    features = summary.get("qemu_features")
    if isinstance(features, dict):
        out = {key: bool(features.get(key, False)) for key in FEATURE_KEYS}
    else:
        out = {key: bool(summary.get(key, False)) for key in FEATURE_KEYS}
    for command_row in summary.get("commands") or []:
        command = command_row.get("command") if isinstance(command_row, dict) else None
        if not isinstance(command, list):
            continue
        tokens = {str(item) for item in command}
        for key, flag in FEATURE_FLAGS.items():
            out[key] = out[key] or flag in tokens
    for qemu_env in _iter_qemu_debug_envs(summary):
        _merge_feature_env(out, qemu_env)
    return out


def _features_from_summary_and_rows(
    summary: dict[str, Any],
    rows: dict[str, dict[str, Any]] | None = None,
) -> dict[str, bool]:
    out = _features_from_summary(summary)
    if rows:
        for qemu_env in _iter_qemu_debug_envs(rows):
            _merge_feature_env(out, qemu_env)
    return out


def _merge_feature_env(out: dict[str, bool], qemu_env: dict[str, Any]) -> None:
    for key, env_name in FEATURE_ENVS.items():
        value = str(qemu_env.get(env_name, "")).strip().lower()
        out[key] = out[key] or bool(value and value not in {"0", "false", "no", "off"})


def _iter_qemu_debug_envs(value: Any) -> list[dict[str, Any]]:
    envs: list[dict[str, Any]] = []
    if isinstance(value, dict):
        env = value.get("qemu_debug_env")
        if isinstance(env, dict):
            envs.append(env)
        for item in value.values():
            envs.extend(_iter_qemu_debug_envs(item))
    elif isinstance(value, list):
        for item in value:
            envs.extend(_iter_qemu_debug_envs(item))
    return envs


def _feature_compatibility(
    gate_summary: dict[str, Any],
    profile_summary: dict[str, Any],
    gate_rows: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    gate = _features_from_summary_and_rows(gate_summary, gate_rows)
    profile = _features_from_summary(profile_summary)
    mismatches = [
        {
            "feature": key,
            "gate": gate[key],
            "profile": profile[key],
        }
        for key in FEATURE_KEYS
        if gate[key] != profile[key]
    ]
    return {
        "ok": not mismatches,
        "gate": gate,
        "profile": profile,
        "mismatches": mismatches,
    }


def build_analysis(
    gate_summary: dict[str, Any],
    profile_summary: dict[str, Any],
    gate_summary_path: Path,
    profile_summary_path: Path,
    *,
    allow_feature_mismatch: bool = False,
) -> dict[str, Any]:
    gate_rows = extract_gate_rows(gate_summary, gate_summary_path)
    feature_compatibility = _feature_compatibility(
        gate_summary,
        profile_summary,
        gate_rows,
    )
    profile_used = bool(feature_compatibility["ok"] or allow_feature_mismatch)
    profile_rows = _profile_by_bench(profile_summary) if profile_used else {}

    rows = [
        _bench_report_row(gate_row, profile_rows.get(bench))
        for bench, gate_row in sorted(gate_rows.items())
    ]
    passing = [row["bench"] for row in rows if row.get("gate_ok")]
    failing = [row["bench"] for row in rows if not row.get("gate_ok")]
    profile_use_reason = (
        "feature-compatible"
        if feature_compatibility["ok"]
        else "allowed-feature-mismatch"
        if allow_feature_mismatch
        else "suppressed-feature-mismatch"
    )

    return {
        "schema_version": "linx-specint-qemu-progress-analysis-v3",
        "generated_at_utc": _utc_now(),
        "gate_summary": str(gate_summary_path),
        "profile_summary": str(profile_summary_path),
        "input_set": (
            gate_summary.get("profile")
            or gate_summary.get("input_set")
            or profile_summary.get("input_set")
        ),
        "stage": profile_summary.get("stage"),
        "qemu": {
            "gate": gate_summary.get("qemu"),
            "profile": profile_summary.get("qemu"),
            "gate_provenance": gate_summary.get("qemu_provenance") or {},
            "profile_provenance": profile_summary.get("qemu_provenance") or {},
            "feature_compatibility": feature_compatibility,
            "profile_used_for_classification": profile_used,
            "profile_use_reason": profile_use_reason,
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
    feature_compatibility = qemu.get("feature_compatibility") or {}
    feature_mismatches = feature_compatibility.get("mismatches") or []
    lines = [
        "# SPECint QEMU Progress Analysis",
        "",
        f"- generated_at_utc: `{report['generated_at_utc']}`",
        f"- input_set: `{report.get('input_set')}`",
        f"- gate_summary: `{report['gate_summary']}`",
        f"- profile_summary: `{report['profile_summary']}`",
        f"- gate_qemu_head: `{gate_head}`",
        f"- profile_qemu_head: `{profile_head}`",
        f"- qemu_feature_compatible: `{str(feature_compatibility.get('ok', True)).lower()}`",
        f"- profile_used_for_classification: `{str(qemu.get('profile_used_for_classification', True)).lower()}`",
        f"- profile_use_reason: `{qemu.get('profile_use_reason', 'unknown')}`",
        "",
    ]
    if feature_mismatches:
        lines.extend(["## QEMU Feature Mismatches", ""])
        for item in feature_mismatches:
            lines.append(
                f"- `{item['feature']}`: gate=`{str(item['gate']).lower()}`, "
                f"profile=`{str(item['profile']).lower()}`"
            )
        lines.append("")

    lines.extend([
        "## Completion",
        "",
        f"- spec_train_correctness_complete: `{str(report['completion_status']['spec_train_correctness_complete']).lower()}`",
        f"- passing_benches: `{', '.join(report['completion_status']['passing_benches'])}`",
        f"- failing_benches: `{', '.join(report['completion_status']['failing_benches'])}`",
        "",
        "## Rows",
        "",
        "| Bench | Transport | Gate | Count | BPC | Progress | Profile | Lane | Top QEMU frames | Next action |",
        "| --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- |",
    ])
    for row in report["benchmarks"]:
        gate = "pass" if row.get("gate_ok") else row.get("failure_class", "fail")
        top = _top_text(row, 5)
        progress = row.get("heartbeat_last_progress", "")
        unique_sites = row.get("heartbeat_recent_unique_sites")
        count_delta = row.get("heartbeat_recent_count_delta")
        progress_text = progress
        if unique_sites is not None or count_delta is not None:
            progress_text = (
                f"{progress or '-'}; sites={unique_sites}; delta={count_delta}"
            )
        lines.append(
            "| "
            f"`{row['bench']}` | "
            f"`{row.get('transport', '')}` | "
            f"`{gate}` | "
            f"{row.get('heartbeat_last_count', '')} | "
            f"`{row.get('heartbeat_last_bpc', '')}` | "
            f"`{progress_text}` | "
            f"`{str(row.get('profile_sample_ok', False)).lower()}` | "
            f"`{row['lane']}` | "
            f"`{top}` | "
            f"{row['proposed_action']} |"
        )

    tlbi_rows = [
        row
        for row in report["benchmarks"]
        if row.get("tlb_inv_hot_kernel_symbol_evidence")
    ]
    if tlbi_rows:
        lines.extend(["", "## TLBI Hot Kernel Evidence", ""])
        for row in tlbi_rows:
            lines.append(
                f"- `{row['bench']}` max-delta=`{row.get('tlb_inv_hot_max_delta')}` "
                f"pc=`{row.get('tlb_inv_hot_max_pc', '')}` "
                f"bpc=`{row.get('tlb_inv_hot_max_bpc', '')}` "
                f"symbols=`{row.get('tlb_inv_hot_kernel_symbol_evidence', '')[:240]}`"
            )

    fault_rows = [
        row
        for row in report["benchmarks"]
        if row.get("trap_seen")
        or row.get("fault_trace_seen")
        or row.get("mem_trace_seen")
        or row.get("syscall_trace_seen")
        or row.get("fentry_trace_seen")
        or row.get("fret_stk_trace_seen")
        or row.get("acre_trace_seen")
        or row.get("queue_trace_seen")
        or row.get("pc_watch_seen")
    ]
    if fault_rows:
        lines.extend(["", "## Fault And Trap Evidence", ""])
        for row in fault_rows:
            lines.append(f"- `{row['bench']}` lane=`{row['lane']}`")
            if row.get("fault_trace_seen"):
                lines.append(
                    f"  fault-trace count=`{row.get('fault_trace_count')}` "
                    f"last=`{row.get('fault_trace_last', '')[:240]}`"
                )
            if row.get("mem_trace_seen"):
                lines.append(
                    f"  mem-trace count=`{row.get('mem_trace_count')}` "
                    f"last=`{row.get('mem_trace_last', '')[:240]}`"
                )
            if row.get("syscall_trace_seen"):
                lines.append(
                    f"  syscall-trace count=`{row.get('syscall_trace_count')}` "
                    f"last=`{row.get('syscall_trace_last', '')[:240]}`"
                )
            if row.get("fentry_trace_seen"):
                lines.append(
                    f"  fentry-trace count=`{row.get('fentry_trace_count')}` "
                    f"last=`{row.get('fentry_trace_last', '')[:240]}`"
                )
            if row.get("fret_stk_trace_seen"):
                lines.append(
                    f"  fret-stk-trace count=`{row.get('fret_stk_trace_count')}` "
                    f"last=`{row.get('fret_stk_trace_last', '')[:240]}`"
                )
            if row.get("acre_trace_seen"):
                lines.append(
                    f"  acre-trace count=`{row.get('acre_trace_count')}` "
                    f"last=`{row.get('acre_trace_last', '')[:240]}`"
                )
            if row.get("queue_trace_seen"):
                lines.append(
                    f"  queue-trace count=`{row.get('queue_trace_count')}` "
                    f"last=`{row.get('queue_trace_last', '')[:240]}`"
                )
            if row.get("pc_watch_seen"):
                lines.append(
                    f"  pc-watch lines=`{row.get('pc_watch_line_count')}` "
                    f"last=`{row.get('pc_watch_last', '')[:240]}`"
                )
                if row.get("pc_watch_ring_seen"):
                    lines.append(
                        f"  pc-watch-ring entries=`{row.get('pc_watch_ring_entry_count')}` "
                        f"last=`{row.get('pc_watch_last_ring_entry', '')[:240]}`"
                    )
            if row.get("child_maps_seen"):
                mapped = row.get("child_maps_trap_addr_mapped")
                mapped_text = "unknown" if mapped is None else str(bool(mapped)).lower()
                lines.append(
                    f"  child-maps trap_addr=`{row.get('child_maps_trap_addr', '')}` "
                    f"mapped=`{mapped_text}` line=`{row.get('child_maps_trap_addr_line', '')[:180]}`"
                )
                fault_mapped = row.get("child_maps_fault_addr_mapped")
                fault_mapped_text = (
                    "unknown" if fault_mapped is None else str(bool(fault_mapped)).lower()
                )
                lines.append(
                    f"  child-maps fault_addr=`{row.get('child_maps_fault_addr', '')}` "
                    f"mapped=`{fault_mapped_text}` line=`{row.get('child_maps_fault_addr_line', '')[:180]}`"
                )
            if row.get("pc_watch_seen"):
                lines.append(f"  pc-watch last=`{row.get('pc_watch_last', '')[:240]}`")
            if row.get("failure_evidence"):
                lines.append(f"  failure=`{row.get('failure_evidence', '')[:240]}`")

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
    parser.add_argument(
        "--allow-feature-mismatch",
        action="store_true",
        help=(
            "Use profile samples for lane classification even when gate/profile "
            "QEMU feature switches differ. By default mismatched profiles are "
            "reported but suppressed from row classification."
        ),
    )
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
        allow_feature_mismatch=args.allow_feature_mismatch,
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
