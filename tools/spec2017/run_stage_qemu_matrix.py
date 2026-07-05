#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
RUNNER = SCRIPT_DIR / "run_int_rate_qemu.py"
BRINGUP_DIR = REPO_ROOT / "tools" / "bringup"
if str(BRINGUP_DIR) not in sys.path:
    sys.path.insert(0, str(BRINGUP_DIR))

from qemu_build_paths import default_qemu_binary, qemu_binary_provenance
QEMU_FAULT_TRACE_FILTER_ARGS = {
    "qemu_fault_trace_pc": "LINX_QEMU_FAULT_TRACE_PC",
    "qemu_fault_trace_pc_lo": "LINX_QEMU_FAULT_TRACE_PC_LO",
    "qemu_fault_trace_pc_hi": "LINX_QEMU_FAULT_TRACE_PC_HI",
    "qemu_fault_trace_addr": "LINX_QEMU_FAULT_TRACE_ADDR",
    "qemu_fault_trace_addr_lo": "LINX_QEMU_FAULT_TRACE_ADDR_LO",
    "qemu_fault_trace_addr_hi": "LINX_QEMU_FAULT_TRACE_ADDR_HI",
    "qemu_fault_trace_count_lo": "LINX_QEMU_FAULT_TRACE_COUNT_LO",
    "qemu_fault_trace_count_hi": "LINX_QEMU_FAULT_TRACE_COUNT_HI",
    "qemu_fault_trace_trapnum": "LINX_QEMU_FAULT_TRACE_TRAPNUM",
}

QEMU_TLB_FAULT_TRACE_FILTER_ARGS = {
    "qemu_tlb_fault_trace_addr": "LINX_QEMU_TLB_FAULT_TRACE_ADDR",
    "qemu_tlb_fault_trace_addr_lo": "LINX_QEMU_TLB_FAULT_TRACE_ADDR_LO",
    "qemu_tlb_fault_trace_addr_hi": "LINX_QEMU_TLB_FAULT_TRACE_ADDR_HI",
    "qemu_tlb_fault_trace_count_lo": "LINX_QEMU_TLB_FAULT_TRACE_COUNT_LO",
    "qemu_tlb_fault_trace_count_hi": "LINX_QEMU_TLB_FAULT_TRACE_COUNT_HI",
}

QEMU_PC_WATCH_ARGS = {
    "qemu_pc_watch": "LINX_DEBUG_PC_WATCH",
    "qemu_pc_watch_count_lo": "LINX_DEBUG_PC_WATCH_COUNT_LO",
    "qemu_pc_watch_count_hi": "LINX_DEBUG_PC_WATCH_COUNT_HI",
    "qemu_pc_watch_hit_limit": "LINX_DEBUG_PC_WATCH_HIT_LIMIT",
    "qemu_pc_watch_hit_lo": "LINX_DEBUG_PC_WATCH_HIT_LO",
    "qemu_pc_watch_hit_hi": "LINX_DEBUG_PC_WATCH_HIT_HI",
    "qemu_pc_watch_match_gpr": "LINX_DEBUG_PC_WATCH_MATCH_GPR",
    "qemu_pc_watch_match_value": "LINX_DEBUG_PC_WATCH_MATCH_VALUE",
    "qemu_pc_watch_match_mask": "LINX_DEBUG_PC_WATCH_MATCH_MASK",
    "qemu_pc_watch_dump_reg": "LINX_DEBUG_PC_WATCH_DUMP_REG",
    "qemu_pc_watch_dump_regs": "LINX_DEBUG_PC_WATCH_DUMP_REGS",
    "qemu_pc_watch_dump_offsets": "LINX_DEBUG_PC_WATCH_DUMP_OFFSETS",
    "qemu_pc_watch_dump_ptr_offsets": "LINX_DEBUG_PC_WATCH_DUMP_PTR_OFFSETS",
    "qemu_pc_watch_dump_words": "LINX_DEBUG_PC_WATCH_DUMP_WORDS",
    "qemu_pc_watch_dump_width": "LINX_DEBUG_PC_WATCH_DUMP_WIDTH",
    "qemu_pc_watch_dump_code_bytes": "LINX_DEBUG_PC_WATCH_DUMP_CODE_BYTES",
    "qemu_pc_watch_ring_size": "LINX_DEBUG_PC_WATCH_RING_SIZE",
    "qemu_pc_watch_ring_mem_reg": "LINX_DEBUG_PC_WATCH_RING_MEM_REG",
    "qemu_pc_watch_ring_mem_offset": "LINX_DEBUG_PC_WATCH_RING_MEM_OFFSET",
}

QEMU_PC_WATCH_BOOL_ARGS = {
    "qemu_pc_watch_regs": "LINX_DEBUG_PC_WATCH_REGS",
    "qemu_pc_watch_ring": "LINX_DEBUG_PC_WATCH_RING",
    "qemu_pc_watch_dump_call_ring": "LINX_DEBUG_PC_WATCH_DUMP_CALL_RING",
    "qemu_pc_watch_dump_phys": "LINX_DEBUG_PC_WATCH_DUMP_PHYS",
}

QEMU_SYSCALL_TRACE_ARGS = {
    "qemu_syscall_trace_nr": "LINX_SYSCALL_TRACE_NR",
    "qemu_syscall_trace_limit": "LINX_SYSCALL_TRACE_LIMIT",
    "qemu_syscall_trace_pc_lo": "LINX_SYSCALL_TRACE_PC_LO",
    "qemu_syscall_trace_pc_hi": "LINX_SYSCALL_TRACE_PC_HI",
    "qemu_syscall_trace_string_max": "LINX_SYSCALL_TRACE_STRING_MAX",
    "qemu_syscall_trace_dump_args": "LINX_SYSCALL_TRACE_DUMP_ARGS",
    "qemu_syscall_trace_dump_arg": "LINX_SYSCALL_TRACE_DUMP_ARG",
    "qemu_syscall_trace_dump_bytes": "LINX_SYSCALL_TRACE_DUMP_BYTES",
}

QEMU_SYSCALL_TRACE_BOOL_ARGS = {
    "qemu_syscall_trace_regs": "LINX_SYSCALL_TRACE_REGS",
    "qemu_syscall_trace_strings": "LINX_SYSCALL_TRACE_STRINGS",
}

QEMU_MEM_TRACE_ARGS = {
    "qemu_mem_trace_addr": "LINX_MEM_TRACE_ADDR",
    "qemu_mem_trace_size": "LINX_MEM_TRACE_SIZE",
    "qemu_mem_trace_limit": "LINX_MEM_TRACE_LIMIT",
    "qemu_mem_trace_access": "LINX_MEM_TRACE_ACCESS",
    "qemu_mem_trace_acr": "LINX_MEM_TRACE_ACR",
    "qemu_mem_trace_pc": "LINX_MEM_TRACE_PC",
    "qemu_mem_trace_pc_lo": "LINX_MEM_TRACE_PC_LO",
    "qemu_mem_trace_pc_hi": "LINX_MEM_TRACE_PC_HI",
    "qemu_mem_trace_count_lo": "LINX_MEM_TRACE_COUNT_LO",
    "qemu_mem_trace_count_hi": "LINX_MEM_TRACE_COUNT_HI",
    "qemu_mem_trace_fast": "LINX_MEM_TRACE_FAST",
}

QEMU_MEM_TRACE_BOOL_ARGS = {
    "qemu_mem_trace_context": "LINX_MEM_TRACE_CONTEXT",
    "qemu_mem_trace_pre": "LINX_MEM_TRACE_PRE",
    "qemu_mem_trace_regs": "LINX_MEM_TRACE_REGS",
}

QEMU_FRET_STK_TRACE_ARGS = {
    "qemu_fret_stk_trace_pc": "LINX_QEMU_FRET_STK_TRACE_PC",
    "qemu_fret_stk_trace_pc_lo": "LINX_QEMU_FRET_STK_TRACE_PC_LO",
    "qemu_fret_stk_trace_pc_hi": "LINX_QEMU_FRET_STK_TRACE_PC_HI",
    "qemu_fret_stk_trace_count_lo": "LINX_QEMU_FRET_STK_TRACE_COUNT_LO",
    "qemu_fret_stk_trace_count_hi": "LINX_QEMU_FRET_STK_TRACE_COUNT_HI",
    "qemu_fret_stk_trace_ra": "LINX_QEMU_FRET_STK_TRACE_RA",
    "qemu_fret_stk_trace_limit": "LINX_QEMU_FRET_STK_TRACE_LIMIT",
    "qemu_fret_stk_trace_dump_words": "LINX_QEMU_FRET_STK_TRACE_DUMP_WORDS",
}

QEMU_FRET_STK_TRACE_BOOL_ARGS = {
    "qemu_fret_stk_trace_regs": "LINX_QEMU_FRET_STK_TRACE_REGS",
}

QEMU_FENTRY_TRACE_ARGS = {
    "qemu_fentry_trace_pc": "LINX_QEMU_FENTRY_TRACE_PC",
    "qemu_fentry_trace_pc_lo": "LINX_QEMU_FENTRY_TRACE_PC_LO",
    "qemu_fentry_trace_pc_hi": "LINX_QEMU_FENTRY_TRACE_PC_HI",
    "qemu_fentry_trace_count_lo": "LINX_QEMU_FENTRY_TRACE_COUNT_LO",
    "qemu_fentry_trace_count_hi": "LINX_QEMU_FENTRY_TRACE_COUNT_HI",
    "qemu_fentry_trace_ra": "LINX_QEMU_FENTRY_TRACE_RA",
    "qemu_fentry_trace_sp": "LINX_QEMU_FENTRY_TRACE_SP",
    "qemu_fentry_trace_new_sp": "LINX_QEMU_FENTRY_TRACE_NEW_SP",
    "qemu_fentry_trace_limit": "LINX_QEMU_FENTRY_TRACE_LIMIT",
    "qemu_fentry_trace_dump_words": "LINX_QEMU_FENTRY_TRACE_DUMP_WORDS",
}

QEMU_FENTRY_TRACE_BOOL_ARGS = {
    "qemu_fentry_trace_regs": "LINX_QEMU_FENTRY_TRACE_REGS",
}


def _default_qemu() -> str:
    env = os.environ.get("QEMU", "").strip()
    if env:
        return str(Path(os.path.expanduser(env)).resolve())
    return str(default_qemu_binary(REPO_ROOT).resolve())


def _qemu_extra_args() -> list[str]:
    return shlex.split(os.environ.get("LINX_SPEC_QEMU_EXTRA_ARGS", ""))


def _default_musl_sysroot() -> str:
    env = os.environ.get("LINX_SYSROOT", "").strip()
    if env:
        return str(Path(os.path.expanduser(env)).resolve())
    phase_c = REPO_ROOT / "out" / "libc" / "musl" / "install" / "phase-c"
    if _usable_static_sysroot(phase_c):
        return str(phase_c.resolve())
    return str((REPO_ROOT / "out" / "libc" / "musl" / "install" / "phase-b").resolve())


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name, "").strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise SystemExit(f"error: {name} must be an integer, got {value!r}") from exc


def _env_float(name: str, default: float) -> float:
    value = os.environ.get(name, "").strip()
    if not value:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise SystemExit(f"error: {name} must be a number, got {value!r}") from exc


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name, "").strip().lower()
    if not value:
        return default
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise SystemExit(f"error: {name} must be a boolean, got {value!r}")


def _usable_static_sysroot(path: Path) -> bool:
    return (
        (path / "usr" / "include" / "errno.h").is_file()
        and (path / "lib" / "libc.a").is_file()
        and (
            (path / "lib" / "rcrt1.o").is_file()
            or (path / "lib" / "crt1.o").is_file()
        )
    )


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _parse_transports(value: str) -> list[str]:
    items = [x.strip() for x in value.split(",") if x.strip()]
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in {"9p", "initramfs"}:
            raise SystemExit(f"error: unsupported transport '{item}' (expected 9p/initramfs)")
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    if not out:
        raise SystemExit("error: --transports resolved to empty set")
    return out


def _default_transports(stage: str) -> list[str]:
    return ["9p", "initramfs"] if stage == "a" else ["9p"]


def _transport_failed_benches(summary_obj: dict[str, Any]) -> list[str]:
    results = summary_obj.get("results", {})
    if not isinstance(results, dict):
        return []
    failed: list[str] = []
    for bench, bench_result in sorted(results.items()):
        ok = isinstance(bench_result, dict) and bool(bench_result.get("ok", False))
        if not ok:
            failed.append(str(bench))
    return failed


def _first_failure_run(qemu_runs: Any) -> dict[str, Any] | None:
    if not isinstance(qemu_runs, list) or not qemu_runs:
        return None
    return next(
        (
            run
            for run in qemu_runs
            if isinstance(run, dict)
            and str(run.get("failure_class") or "none") != "none"
        ),
        next((run for run in qemu_runs if isinstance(run, dict)), None),
    )


def _transport_failure_classes(summary_obj: dict[str, Any]) -> dict[str, str]:
    results = summary_obj.get("results", {})
    if not isinstance(results, dict):
        return {}

    classes: dict[str, str] = {}
    for bench, bench_result in sorted(results.items()):
        if not isinstance(bench_result, dict) or bool(bench_result.get("ok", False)):
            continue
        qemu_runs = bench_result.get("qemu", [])
        if not isinstance(qemu_runs, list) or not qemu_runs:
            if bench_result.get("error"):
                classes[str(bench)] = "runner-error"
            continue
        failed_run = _first_failure_run(qemu_runs)
        if isinstance(failed_run, dict):
            classes[str(bench)] = str(failed_run.get("failure_class") or "unclassified")
    return classes


def _transport_failure_details(summary_obj: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results = summary_obj.get("results", {})
    if not isinstance(results, dict):
        return {}

    details: dict[str, dict[str, Any]] = {}
    for bench, bench_result in sorted(results.items()):
        if not isinstance(bench_result, dict) or bool(bench_result.get("ok", False)):
            continue
        qemu_runs = bench_result.get("qemu", [])
        if not isinstance(qemu_runs, list) or not qemu_runs:
            if bench_result.get("error"):
                details[str(bench)] = {
                    "failure_class": "runner-error",
                    "failure_evidence": str(bench_result.get("error", ""))[:512],
                    "heartbeat_running": False,
                    "heartbeat_site_progress": False,
                }
            continue
        failed_run = _first_failure_run(qemu_runs)
        if not isinstance(failed_run, dict):
            continue
        details[str(bench)] = {
            "failure_class": str(failed_run.get("failure_class") or "unclassified"),
            "failure_evidence": str(failed_run.get("failure_evidence") or "")[:512],
            "qemu_machine": str(failed_run.get("qemu_machine") or ""),
            "qemu_machine_extra": str(failed_run.get("qemu_machine_extra") or ""),
            "qemu_extra_args": failed_run.get("qemu_extra_args") or [],
            "timed_out": bool(failed_run.get("timed_out", False)),
            "stalled": bool(failed_run.get("stalled", False)),
            "panic_seen": bool(failed_run.get("panic_seen", False)),
            "trap_seen": bool(failed_run.get("trap_seen", False)),
            "run_index": failed_run.get("run_index"),
            "heartbeat_running": bool(failed_run.get("heartbeat_running", False)),
            "heartbeat_site_progress": bool(failed_run.get("heartbeat_site_progress", False)),
            "heartbeat_last_count": failed_run.get("heartbeat_last_count"),
            "heartbeat_last_bpc": str(failed_run.get("heartbeat_last_bpc") or ""),
            "heartbeat_last_progress": str(failed_run.get("heartbeat_last_progress") or ""),
            "heartbeat_last_same_site": failed_run.get("heartbeat_last_same_site"),
            "heartbeat_recent_unique_sites": failed_run.get("heartbeat_recent_unique_sites"),
            "heartbeat_recent_count_delta": failed_run.get("heartbeat_recent_count_delta"),
            "heartbeat_stall_seen": bool(failed_run.get("heartbeat_stall_seen", False)),
            "heartbeat_stall_count": failed_run.get("heartbeat_stall_count"),
            "heartbeat_stall_last": str(failed_run.get("heartbeat_stall_last") or "")[:512],
            "heartbeat_stall_repeats": failed_run.get("heartbeat_stall_repeats"),
            "heartbeat_stall_threshold": failed_run.get("heartbeat_stall_threshold"),
            "heartbeat_stall_bpc": str(failed_run.get("heartbeat_stall_bpc") or ""),
            "heartbeat_stall_status": str(failed_run.get("heartbeat_stall_status") or ""),
            "heartbeat_tlb_fill": failed_run.get("heartbeat_tlb_fill") or {},
            "heartbeat_mmu_cache": failed_run.get("heartbeat_mmu_cache") or {},
            "heartbeat_frame_stats": failed_run.get("heartbeat_frame_stats") or {},
            "heartbeat_frame_shape_hot": failed_run.get("heartbeat_frame_shape_hot") or {},
            "heartbeat_tlb_invalidation": failed_run.get("heartbeat_tlb_invalidation") or {},
            "heartbeat_tb_stats": failed_run.get("heartbeat_tb_stats") or {},
            "heartbeat_tlb_fill_hot": failed_run.get("heartbeat_tlb_fill_hot") or {},
            "heartbeat_tlb_inv_hot": failed_run.get("heartbeat_tlb_inv_hot") or {},
            "bstart_cache_stats": failed_run.get("bstart_cache_stats") or {},
            "pc_watch": failed_run.get("pc_watch") or {},
            "heartbeat_kernel_symbolized": bool(failed_run.get("heartbeat_kernel_symbolized", False)),
            "heartbeat_kernel_panic_loop": bool(failed_run.get("heartbeat_kernel_panic_loop", False)),
            "heartbeat_kernel_symbol_evidence": str(failed_run.get("heartbeat_kernel_symbol_evidence") or "")[:512],
            "heartbeat_kernel_symbols": failed_run.get("heartbeat_kernel_symbols") or [],
            "last_heartbeat": str(failed_run.get("last_heartbeat") or "")[:512],
            "fcmp_trace_seen": bool(failed_run.get("fcmp_trace_seen", False)),
            "fcmp_trace_count": failed_run.get("fcmp_trace_count"),
            "fcmp_trace_last": str(failed_run.get("fcmp_trace_last") or "")[:512],
            "fcmp_trace_samples": failed_run.get("fcmp_trace_samples") or [],
            "tlb_fill_trace_seen": bool(failed_run.get("tlb_fill_trace_seen", False)),
            "tlb_fill_trace_count": failed_run.get("tlb_fill_trace_count"),
            "tlb_fill_trace_last": str(failed_run.get("tlb_fill_trace_last") or "")[:512],
            "tlb_fill_trace_samples": failed_run.get("tlb_fill_trace_samples") or [],
            "tlb_fault_trace_seen": bool(failed_run.get("tlb_fault_trace_seen", False)),
            "tlb_fault_trace_count": failed_run.get("tlb_fault_trace_count"),
            "tlb_fault_trace_last": str(failed_run.get("tlb_fault_trace_last") or "")[:512],
            "tlb_fault_trace_samples": failed_run.get("tlb_fault_trace_samples") or [],
            "mprotect_trace_seen": bool(failed_run.get("mprotect_trace_seen", False)),
            "mprotect_trace_count": failed_run.get("mprotect_trace_count"),
            "mprotect_trace_last": str(failed_run.get("mprotect_trace_last") or "")[:512],
            "mprotect_trace_samples": failed_run.get("mprotect_trace_samples") or [],
            "log": str(failed_run.get("log") or ""),
        }
    return details


def _format_tlb_fill_hot(row: dict[str, Any]) -> str:
    hot = row.get("heartbeat_tlb_fill_hot")
    if not isinstance(hot, dict) or not hot.get("seen"):
        return ""
    top0_count = hot.get("top0_count")
    if top0_count is None:
        return ""
    page = hot.get("top0_page") or "no-page"
    access = hot.get("top0_access")
    mmu = hot.get("top0_mmu")
    evictions = hot.get("evictions")
    return f" tlbf-hot={top0_count}@{page}/a{access}/m{mmu} evict={evictions}"


def _format_tlb_inv_hot(row: dict[str, Any]) -> str:
    hot = row.get("heartbeat_tlb_inv_hot")
    if not isinstance(hot, dict) or not hot.get("seen"):
        return ""
    top0_count = hot.get("max_delta_top0_count")
    if top0_count is None:
        top0_count = hot.get("top0_count")
    if top0_count is None:
        return ""
    top0_delta = hot.get("max_delta_top0_delta")
    if top0_delta is None:
        top0_delta = hot.get("top0_delta")
    count_tag = f"{top0_delta}/{top0_count}" if top0_delta is not None else str(top0_count)
    op = hot.get("max_delta_top0_op") or hot.get("top0_op") or f"op{hot.get('top0_opid')}"
    pc = hot.get("max_delta_top0_pc") or hot.get("top0_pc") or "no-pc"
    page = hot.get("max_delta_top0_page") or hot.get("top0_page") or "no-page"
    evictions = hot.get("evictions")
    return f" tlbi-hot={count_tag}:{op}@{pc}/page{page} evict={evictions}"


def _format_bstart_cache_stats(row: dict[str, Any]) -> str:
    stats = row.get("bstart_cache_stats")
    if not isinstance(stats, dict) or not stats.get("seen"):
        return ""
    return (
        f" bstart-cache={stats.get('hits')}/{stats.get('checks')}"
        f" hit={stats.get('hit_pct')}%"
        f" miss={stats.get('bstarts')}"
        f" reset={stats.get('resets')}/{stats.get('page_resets')}"
    )


def _format_pc_watch(row: dict[str, Any]) -> str:
    stats = row.get("pc_watch")
    if not isinstance(stats, dict) or not stats.get("seen"):
        return ""
    ring = ""
    if stats.get("ring_seen"):
        ring = (
            f"/ring{stats.get('ring_count')}"
            f"/entries{stats.get('ring_entry_count')}"
        )
    mem = ""
    last_entry = stats.get("last_ring_entry_fields")
    if isinstance(last_entry, dict) and last_entry.get("mem_ok") is not None:
        mem = (
            f"/mem{last_entry.get('mem_ok')}"
            f"@{last_entry.get('mem_addr') or 'no-addr'}"
            f"={last_entry.get('mem_value') or 'no-value'}"
        )
    return f" pc-watch={stats.get('line_count')}{ring}{mem}"


def _format_mmu_cache_stats(row: dict[str, Any]) -> str:
    stats = row.get("heartbeat_mmu_cache")
    if not isinstance(stats, dict) or stats.get("hit") is None:
        return ""
    return (
        f" mmuc=h{stats.get('hit')}"
        f"/m{stats.get('miss')}"
        f"/f{stats.get('fill')}"
        f"/flush{stats.get('flush')}"
        f"/pflush{stats.get('flush_page')}"
    )


def _format_frame_stats(row: dict[str, Any]) -> str:
    stats = row.get("heartbeat_frame_stats")
    if not isinstance(stats, dict) or stats.get("fentry") is None:
        return ""
    return (
        f" frame=fentry{stats.get('fentry')}"
        f"/save{stats.get('save_slot')}"
        f"/host{stats.get('save_host')}"
        f"/fb{stats.get('save_fallback')}"
        f" restore{stats.get('restore_slot')}"
        f"/host{stats.get('restore_host')}"
        f"/fb{stats.get('restore_fallback')}"
        f" ret{stats.get('ret_fast')}/{stats.get('ret_check')}"
    )


def _format_frame_shape_hot(row: dict[str, Any]) -> str:
    hot = row.get("heartbeat_frame_shape_hot")
    if (
        not isinstance(hot, dict)
        or not hot.get("seen")
        or hot.get("top0_count") is None
    ):
        return ""
    top0_count = hot.get("max_delta_top0_count")
    if top0_count is None:
        top0_count = hot.get("top0_count")
    top0_delta = hot.get("max_delta_top0_delta")
    if top0_delta is None:
        top0_delta = hot.get("top0_delta")
    kind = hot.get("max_delta_top0_kind") or hot.get("top0_kind") or "shape"
    begin = hot.get("max_delta_top0_begin")
    if begin is None:
        begin = hot.get("top0_begin")
    end = hot.get("max_delta_top0_end")
    if end is None:
        end = hot.get("top0_end")
    stack = hot.get("max_delta_top0_stack")
    if stack is None:
        stack = hot.get("top0_stack")
    regs = hot.get("max_delta_top0_regs")
    if regs is None:
        regs = hot.get("top0_regs")
    return (
        f" frame-hot={kind}:{top0_count}"
        f"/d{top0_delta}"
        f"/r{begin}-{end}"
        f"/n{regs}"
        f"/s{stack}"
        f" evict={hot.get('evictions')}"
    )


def _format_tlb_invalidation_stats(row: dict[str, Any]) -> str:
    stats = row.get("heartbeat_tlb_invalidation")
    if not isinstance(stats, dict) or stats.get("iv") is None:
        return ""
    last = ""
    last_bpc = stats.get("last_bpc")
    last_operand = stats.get("last_operand")
    if last_bpc or last_operand:
        last = f" last={last_bpc or 'no-bpc'}@{last_operand or 'no-op'}"
    return (
        f" tlbi=iv{stats.get('iv')}"
        f"/iav{stats.get('iav')}"
        f"/ia{stats.get('ia')}"
        f"/iall{stats.get('iall')}"
        f"{last}"
    )


def _format_tb_stats(row: dict[str, Any]) -> str:
    stats = row.get("heartbeat_tb_stats")
    if not isinstance(stats, dict) or stats.get("lookup") is None:
        return ""
    return (
        f" tb=exec{stats.get('exec')}"
        f"/lookup{stats.get('lookup')}"
        f"/jmp{stats.get('jmp_hit')}"
        f"/hash{stats.get('hash_hit')}"
        f"/miss{stats.get('miss')}"
        f"/gen{stats.get('gen')}"
        f" flush{stats.get('flush')}"
        f" inv{stats.get('phys_inv')}"
        f" code{stats.get('code_used')}/{stats.get('code_size')}"
    )


def _format_failure_details(details: dict[str, dict[str, Any]]) -> str:
    if not details:
        return "-"
    parts: list[str] = []
    for bench, row in sorted(details.items()):
        running = "running" if row.get("heartbeat_running") else "not-running"
        site = "site-progress" if row.get("heartbeat_site_progress") else "same-site"
        bpc = row.get("heartbeat_last_bpc") or "no-bpc"
        progress = row.get("heartbeat_last_progress") or "no-progress-tag"
        unique_sites = row.get("heartbeat_recent_unique_sites")
        count_delta = row.get("heartbeat_recent_count_delta")
        recent = ""
        if unique_sites is not None or count_delta is not None:
            recent = f" recent-sites={unique_sites} count-delta={count_delta}"
        fcmp = ""
        if row.get("fcmp_trace_seen"):
            fcmp = f" fcmp-trace={row.get('fcmp_trace_count')}"
        tlbfill = ""
        if row.get("tlb_fill_trace_seen"):
            tlbfill = f" tlbfill-trace={row.get('tlb_fill_trace_count')}"
        tlbfault = ""
        if row.get("tlb_fault_trace_seen"):
            tlbfault = f" tlbfault-trace={row.get('tlb_fault_trace_count')}"
        tlbfill_stats = ""
        heartbeat_tlb_fill = row.get("heartbeat_tlb_fill")
        if isinstance(heartbeat_tlb_fill, dict) and heartbeat_tlb_fill.get("total") is not None:
            tlbfill_stats = (
                f" tlbf={heartbeat_tlb_fill.get('total')}"
                f"/f{heartbeat_tlb_fill.get('fetch')}"
                f"/l{heartbeat_tlb_fill.get('load')}"
                f"/s{heartbeat_tlb_fill.get('store')}"
                f"/p{heartbeat_tlb_fill.get('probe')}"
            )
            if heartbeat_tlb_fill.get("user") is not None:
                tlbfill_stats += (
                    f"/u{heartbeat_tlb_fill.get('user')}"
                    f"/k{heartbeat_tlb_fill.get('kernel')}"
                    f"/o{heartbeat_tlb_fill.get('other')}"
                )
        tlbfill_hot = _format_tlb_fill_hot(row)
        tlbinv_hot = _format_tlb_inv_hot(row)
        mmu_cache = _format_mmu_cache_stats(row)
        frame_stats = _format_frame_stats(row)
        frame_shape_hot = _format_frame_shape_hot(row)
        tlb_invalidation = _format_tlb_invalidation_stats(row)
        tb_stats = _format_tb_stats(row)
        bstart_cache = _format_bstart_cache_stats(row)
        pc_watch = _format_pc_watch(row)
        mprotect = ""
        if row.get("mprotect_trace_seen"):
            mprotect = f" mprotect-trace={row.get('mprotect_trace_count')}"
        kernel = ""
        if row.get("heartbeat_kernel_panic_loop"):
            kernel = " kernel-panic-loop"
        elif row.get("heartbeat_kernel_symbol_evidence"):
            kernel = " kernel-symbolized"
        timeout = " timeout" if row.get("timed_out") else ""
        stalled = " stalled" if row.get("stalled") else ""
        hb_stall = ""
        if row.get("heartbeat_stall_seen"):
            repeats = row.get("heartbeat_stall_repeats")
            threshold = row.get("heartbeat_stall_threshold")
            status = row.get("heartbeat_stall_status") or "same-site"
            hb_stall = f" heartbeat-stall={status}:{repeats}/{threshold}"
        parts.append(
            f"{bench}: {running}/{site} {progress}{timeout}{stalled} "
            f"bpc={bpc}{recent}{kernel}{hb_stall}{fcmp}{tlbfill}{tlbfault}{tlbfill_stats}{tlbfill_hot}{mmu_cache}{frame_stats}{frame_shape_hot}{tlb_invalidation}{tlbinv_hot}{tb_stats}{bstart_cache}{mprotect}"
            f"{pc_watch}"
        )
    return ", ".join(parts)


def _write_md(path: Path, summary: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# SPEC QEMU Matrix Summary")
    lines.append("")
    lines.append("## Run")
    lines.append("")
    lines.append(f"- stage: `{summary['stage']}`")
    lines.append(f"- input_set: `{summary['input_set']}`")
    lines.append(f"- strict: `{str(summary['strict']).lower()}`")
    lines.append(f"- transports: `{', '.join(summary['transports'])}`")
    qemu_provenance = summary.get("qemu_provenance") or {}
    if qemu_provenance:
        lines.append(f"- qemu: `{qemu_provenance.get('path', '-')}`")
        lines.append(f"- qemu_version: `{qemu_provenance.get('version', '-')}`")
        lines.append(f"- qemu_repo_head: `{qemu_provenance.get('qemu_repo_head', '-')}`")
        lines.append(
            "- qemu_clean_build_for_head: "
            f"`{str(bool(qemu_provenance.get('clean_build_for_head', False))).lower()}`"
        )
    qemu_machine_extra = str(summary.get("qemu_machine_extra") or "")
    qemu_extra_args = summary.get("qemu_extra_args") or []
    qemu_extra_text = shlex.join([str(arg) for arg in qemu_extra_args]) if qemu_extra_args else "-"
    lines.append(f"- qemu_machine_extra: `{qemu_machine_extra or '-'}`")
    lines.append(f"- qemu_extra_args: `{qemu_extra_text}`")
    lines.append(f"- timeout_sec: `{summary['timeout_sec']}`")
    lines.append(f"- fail_9p_timeout: `{str(bool(summary.get('fail_9p_timeout', False))).lower()}`")
    lines.append(f"- memory_mb: `{summary['memory_mb']}`")
    lines.append(f"- stack_limit: `{summary['stack_limit']}`")
    lines.append(f"- append_extra: `{summary['append_extra'] or '-'}`")
    lines.append(f"- qemu_heartbeat_interval: `{summary['qemu_heartbeat_interval']}`")
    lines.append(f"- qemu_heartbeat_regs: `{str(bool(summary.get('qemu_heartbeat_regs', False))).lower()}`")
    lines.append(f"- qemu_heartbeat_code_bytes: `{summary.get('qemu_heartbeat_code_bytes', 0)}`")
    lines.append(f"- qemu_heartbeat_same_site_warn: `{summary.get('qemu_heartbeat_same_site_warn', 0)}`")
    lines.append(f"- qemu_frame_stats: `{str(bool(summary.get('qemu_frame_stats', False))).lower()}`")
    lines.append(f"- qemu_frame_shape_hot: `{str(bool(summary.get('qemu_frame_shape_hot', False))).lower()}`")
    lines.append(f"- qemu_frame_single_reg_fast: `{str(bool(summary.get('qemu_frame_single_reg_fast', False))).lower()}`")
    lines.append(
        "- qemu_frame_restore_host_load: "
        f"`{str(bool(summary.get('qemu_frame_restore_host_load', False))).lower()}`"
    )
    lines.append(
        "- qemu_frame_restore_host_verify: "
        f"`{str(bool(summary.get('qemu_frame_restore_host_verify', False))).lower()}`"
    )
    lines.append(
        "- qemu_frame_restore_host_verify_limit: "
        f"`{summary.get('qemu_frame_restore_host_verify_limit', 0)}`"
    )
    fret_stk_trace = summary.get("qemu_fret_stk_trace") or {}
    if fret_stk_trace:
        trace_text = ", ".join(f"{k}={v}" for k, v in sorted(fret_stk_trace.items()))
        lines.append(f"- qemu_fret_stk_trace: `{trace_text}`")
    fentry_trace = summary.get("qemu_fentry_trace") or {}
    if fentry_trace:
        trace_text = ", ".join(f"{k}={v}" for k, v in sorted(fentry_trace.items()))
        lines.append(f"- qemu_fentry_trace: `{trace_text}`")
    lines.append(f"- qemu_tlb_stats: `{str(bool(summary.get('qemu_tlb_stats', False))).lower()}`")
    lines.append(f"- qemu_tlb_inv_hot: `{str(bool(summary.get('qemu_tlb_inv_hot', False))).lower()}`")
    lines.append(f"- qemu_tlb_fill_stats: `{str(bool(summary.get('qemu_tlb_fill_stats', False))).lower()}`")
    lines.append(f"- qemu_tlb_fill_hot: `{str(bool(summary.get('qemu_tlb_fill_hot', False))).lower()}`")
    lines.append(f"- qemu_mmu_cache: `{str(bool(summary.get('qemu_mmu_cache', False))).lower()}`")
    lines.append(f"- qemu_mmu_cache_stats: `{str(bool(summary.get('qemu_mmu_cache_stats', False))).lower()}`")
    lines.append(f"- qemu_tb_stats: `{str(bool(summary.get('qemu_tb_stats', False))).lower()}`")
    lines.append(f"- qemu_fault_trace: `{str(bool(summary.get('qemu_fault_trace', False))).lower()}`")
    lines.append(f"- qemu_fault_trace_regs: `{str(bool(summary.get('qemu_fault_trace_regs', False))).lower()}`")
    lines.append(f"- qemu_fault_trace_limit: `{summary.get('qemu_fault_trace_limit', 1)}`")
    filters = summary.get("qemu_fault_trace_filters") or {}
    if filters:
        filter_text = ", ".join(f"{k}={v}" for k, v in sorted(filters.items()))
        lines.append(f"- qemu_fault_trace_filters: `{filter_text}`")
    pc_watch = summary.get("qemu_pc_watch") or {}
    if pc_watch:
        watch_text = ", ".join(f"{k}={v}" for k, v in sorted(pc_watch.items()))
        lines.append(f"- qemu_pc_watch: `{watch_text}`")
    syscall_trace = summary.get("qemu_syscall_trace") or {}
    if syscall_trace:
        trace_text = ", ".join(f"{k}={v}" for k, v in sorted(syscall_trace.items()))
        lines.append(f"- qemu_syscall_trace: `{trace_text}`")
    mem_trace = summary.get("qemu_mem_trace") or {}
    if mem_trace:
        trace_text = ", ".join(f"{k}={v}" for k, v in sorted(mem_trace.items()))
        lines.append(f"- qemu_mem_trace: `{trace_text}`")
    lines.append(f"- guest_heartbeat_sec: `{summary['guest_heartbeat_sec']}`")
    guest_proc_diag = str(bool(summary.get("guest_proc_diagnostics", False))).lower()
    lines.append(f"- guest_proc_diagnostics: `{guest_proc_diag}`")
    if summary.get("bench_override"):
        benches = ", ".join(summary["bench_override"])
        lines.append(f"- bench_override: `{benches}`")
    lines.append(f"- ok: `{str(summary['ok']).lower()}`")
    lines.append(f"- elapsed_sec: `{summary['elapsed_sec']}`")
    lines.append("")
    lines.append("## Transport Results")
    lines.append("")
    lines.append("| Transport | OK | Return | Failed Benches | Failure Classes | Liveness | Summary | Log |")
    lines.append("|---|---:|---:|---|---|---|---|---|")

    for row in summary.get("results", []):
        failed_benches = row.get("failed_benches", [])
        failed_text = ", ".join(failed_benches) if failed_benches else "-"
        failure_classes = row.get("failure_classes", {})
        if isinstance(failure_classes, dict) and failure_classes:
            classes_text = ", ".join(
                f"{bench}: {cls}" for bench, cls in sorted(failure_classes.items())
            )
        else:
            classes_text = "-"
        details = row.get("failure_details", {})
        details_text = _format_failure_details(details if isinstance(details, dict) else {})
        lines.append(
            "| "
            f"`{row.get('transport', '')}` | "
            f"`{str(bool(row.get('ok', False))).lower()}` | "
            f"`{row.get('returncode', 'n/a')}` | "
            f"`{failed_text}` | "
            f"`{classes_text}` | "
            f"`{details_text}` | "
            f"`{row.get('summary_json', '')}` | "
            f"`{row.get('log', '')}` |"
        )

    lines.append("")
    if summary.get("failed_transports"):
        lines.append("## Failed Transports")
        lines.append("")
        for item in summary["failed_transports"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("## Failed Transports")
        lines.append("")
        lines.append("- none")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Run SPEC stage matrix across QEMU transports.")
    ap.add_argument(
        "--spec-dir",
        default=str(REPO_ROOT / "workloads" / "spec2017" / "cpu2017v118_x64_gcc12_avx2"),
    )
    ap.add_argument(
        "--qemu",
        default=_default_qemu(),
        help="QEMU binary passed through to the per-transport runner.",
    )
    ap.add_argument("--stage", choices=("a", "b"), default="a")
    ap.add_argument("--input-set", choices=("refrate", "test", "train"), default="test")
    ap.add_argument(
        "--transports",
        default="",
        help="Comma-separated transport list. Defaults: stage-a=9p,initramfs; stage-b=9p.",
    )
    ap.add_argument("--bench", action="append", help="Optional bench override; repeatable.")
    ap.add_argument("--strict", action="store_true", help="Fail if any transport/bench fails.")
    ap.add_argument("--sysroot", default=_default_musl_sysroot(), help="Linx sysroot passed through to the per-transport runner.")
    ap.add_argument(
        "--timeout",
        type=int,
        default=_env_int("LINX_SPEC_QEMU_TIMEOUT", 1200),
        help="Per-transport runner timeout in seconds (default: LINX_SPEC_QEMU_TIMEOUT or 1200).",
    )
    ap.add_argument(
        "--memory-mb",
        type=int,
        default=_env_int("LINX_SPEC_MEMORY_MB", 2048),
        help="Guest memory in MiB passed through to qemu-system-linx64.",
    )
    ap.add_argument(
        "--stack-limit",
        default=os.environ.get(
            "SPEC_STACK_LIMIT",
            os.environ.get("LINX_SPEC_STACK_LIMIT_BYTES", os.environ.get("LINX_SPEC_STACK_LIMIT", "")),
        ),
        help="SPEC init wrapper stack limit passed through to the per-transport runner.",
    )
    ap.add_argument(
        "--heartbeat-sec",
        type=float,
        default=_env_float("LINX_SPEC_HEARTBEAT_SEC", 30.0),
        help="Host heartbeat interval passed through to the per-transport runner (0 disables).",
    )
    ap.add_argument(
        "--qemu-heartbeat-interval",
        type=int,
        default=_env_int("LINX_SPEC_QEMU_HEARTBEAT_INTERVAL", 0),
        help="QEMU BPC heartbeat interval passed through to the per-transport runner (0 disables).",
    )
    ap.add_argument(
        "--qemu-heartbeat-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_HEARTBEAT_REGS", False),
        help="Pass --qemu-heartbeat-regs to the per-transport runner.",
    )
    ap.add_argument(
        "--qemu-heartbeat-code-bytes",
        type=int,
        default=_env_int("LINX_SPEC_QEMU_HEARTBEAT_CODE_BYTES", 0),
        help="QEMU heartbeat PC/BPC code bytes passed through to the per-transport runner (0 disables).",
    )
    ap.add_argument(
        "--qemu-heartbeat-same-site-warn",
        type=int,
        default=_env_int("LINX_SPEC_QEMU_HEARTBEAT_SAME_SITE_WARN", 0),
        help="QEMU same-site heartbeat warning threshold passed through to the per-transport runner (0 disables).",
    )
    ap.add_argument(
        "--qemu-frame-stats",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FRAME_STATS", False),
        help="Pass --qemu-frame-stats to append frame-template counters to QEMU heartbeats.",
    )
    ap.add_argument(
        "--qemu-frame-shape-hot",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FRAME_SHAPE_HOT", False),
        help="Pass --qemu-frame-shape-hot to emit hot frame-template shape heartbeat sketches.",
    )
    ap.add_argument(
        "--qemu-frame-single-reg-fast",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FRAME_SINGLE_REG_FAST", False),
        help="Pass --qemu-frame-single-reg-fast to enable QEMU's opt-in one-register frame fast path.",
    )
    ap.add_argument(
        "--qemu-frame-restore-host-load",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FRAME_RESTORE_HOST_LOAD", False),
        help="Pass --qemu-frame-restore-host-load to enable cached host loads for frame restore slots.",
    )
    ap.add_argument(
        "--qemu-frame-restore-host-verify",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FRAME_RESTORE_HOST_VERIFY", False),
        help="Pass --qemu-frame-restore-host-verify to compare host restore loads against soft-MMU loads.",
    )
    ap.add_argument(
        "--qemu-frame-restore-host-verify-limit",
        type=int,
        default=_env_int("LINX_SPEC_QEMU_FRAME_RESTORE_HOST_VERIFY_LIMIT", 0),
        help="Pass --qemu-frame-restore-host-verify-limit to cap mismatch trace lines (0 uses QEMU default).",
    )
    ap.add_argument(
        "--qemu-fret-stk-trace",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FRET_STK_TRACE", False),
        help="Pass --qemu-fret-stk-trace to enable FRET.STK frame-restore tracing.",
    )
    ap.add_argument(
        "--qemu-fret-stk-trace-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FRET_STK_TRACE_REGS", False),
        help="Pass --qemu-fret-stk-trace-regs to dump GPRs on FRET.STK trace hits.",
    )
    ap.add_argument("--qemu-fret-stk-trace-pc", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_PC", ""))
    ap.add_argument("--qemu-fret-stk-trace-pc-lo", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_PC_LO", ""))
    ap.add_argument("--qemu-fret-stk-trace-pc-hi", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_PC_HI", ""))
    ap.add_argument("--qemu-fret-stk-trace-count-lo", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_COUNT_LO", ""))
    ap.add_argument("--qemu-fret-stk-trace-count-hi", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_COUNT_HI", ""))
    ap.add_argument("--qemu-fret-stk-trace-ra", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_RA", ""))
    ap.add_argument("--qemu-fret-stk-trace-limit", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_LIMIT", ""))
    ap.add_argument("--qemu-fret-stk-trace-dump-words", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_DUMP_WORDS", ""))
    ap.add_argument(
        "--qemu-fentry-trace",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FENTRY_TRACE", False),
        help="Pass --qemu-fentry-trace to enable FENTRY frame-save tracing.",
    )
    ap.add_argument(
        "--qemu-fentry-trace-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FENTRY_TRACE_REGS", False),
        help="Pass --qemu-fentry-trace-regs to dump GPRs on FENTRY trace hits.",
    )
    ap.add_argument("--qemu-fentry-trace-pc", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_PC", ""))
    ap.add_argument("--qemu-fentry-trace-pc-lo", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_PC_LO", ""))
    ap.add_argument("--qemu-fentry-trace-pc-hi", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_PC_HI", ""))
    ap.add_argument("--qemu-fentry-trace-count-lo", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_COUNT_LO", ""))
    ap.add_argument("--qemu-fentry-trace-count-hi", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_COUNT_HI", ""))
    ap.add_argument("--qemu-fentry-trace-ra", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_RA", ""))
    ap.add_argument("--qemu-fentry-trace-sp", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_SP", ""))
    ap.add_argument("--qemu-fentry-trace-new-sp", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_NEW_SP", ""))
    ap.add_argument("--qemu-fentry-trace-limit", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_LIMIT", ""))
    ap.add_argument("--qemu-fentry-trace-dump-words", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_DUMP_WORDS", ""))
    ap.add_argument(
        "--qemu-tlb-stats",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_TLB_STATS", False),
        help="Pass --qemu-tlb-stats to append TLB invalidation counters to QEMU heartbeats.",
    )
    ap.add_argument(
        "--qemu-tlb-inv-hot",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_TLB_INV_HOT", False),
        help="Pass --qemu-tlb-inv-hot to emit TLBI source-PC hot-site heartbeat lines.",
    )
    ap.add_argument(
        "--qemu-tlb-fill-stats",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_TLB_FILL_STATS", False),
        help="Pass --qemu-tlb-fill-stats to append demand page-walk counters to QEMU heartbeats.",
    )
    ap.add_argument(
        "--qemu-tlb-fill-hot",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_TLB_FILL_HOT", False),
        help="Pass --qemu-tlb-fill-hot to emit hot demand page-walk heartbeat sketches.",
    )
    ap.add_argument(
        "--qemu-mmu-cache",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_MMU_CACHE", False),
        help="Pass --qemu-mmu-cache to enable QEMU's opt-in page-walk result cache.",
    )
    ap.add_argument(
        "--qemu-mmu-cache-stats",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_MMU_CACHE_STATS", False),
        help="Pass --qemu-mmu-cache-stats to append MMU-cache counters to QEMU heartbeats.",
    )
    ap.add_argument(
        "--qemu-tlb-fault-trace",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_TLB_FAULT_TRACE", False),
        help="Pass --qemu-tlb-fault-trace to emit page-walk fault diagnostics.",
    )
    ap.add_argument(
        "--qemu-tlb-fault-trace-limit",
        type=int,
        default=_env_int("LINX_SPEC_QEMU_TLB_FAULT_TRACE_LIMIT", 0),
        help="Pass --qemu-tlb-fault-trace-limit to cap TLB fault trace lines.",
    )
    ap.add_argument("--qemu-tlb-fault-trace-addr", default=os.environ.get("LINX_SPEC_QEMU_TLB_FAULT_TRACE_ADDR", ""))
    ap.add_argument("--qemu-tlb-fault-trace-addr-lo", default=os.environ.get("LINX_SPEC_QEMU_TLB_FAULT_TRACE_ADDR_LO", ""))
    ap.add_argument("--qemu-tlb-fault-trace-addr-hi", default=os.environ.get("LINX_SPEC_QEMU_TLB_FAULT_TRACE_ADDR_HI", ""))
    ap.add_argument("--qemu-tlb-fault-trace-count-lo", default=os.environ.get("LINX_SPEC_QEMU_TLB_FAULT_TRACE_COUNT_LO", ""))
    ap.add_argument("--qemu-tlb-fault-trace-count-hi", default=os.environ.get("LINX_SPEC_QEMU_TLB_FAULT_TRACE_COUNT_HI", ""))
    ap.add_argument(
        "--qemu-tb-stats",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_TB_STATS", False),
        help="Pass --qemu-tb-stats to append TCG TB counters to QEMU heartbeats.",
    )
    ap.add_argument(
        "--qemu-fault-trace",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FAULT_TRACE", False),
        help="Enable QEMU fault tracing in per-transport runners without forcing GPR dumps.",
    )
    ap.add_argument(
        "--qemu-fault-trace-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FAULT_TRACE_REGS", False),
        help="Enable QEMU fault tracing plus full GPR dumps in per-transport runners.",
    )
    ap.add_argument(
        "--qemu-fault-trace-limit",
        type=int,
        default=_env_int("LINX_SPEC_QEMU_FAULT_TRACE_LIMIT", 1),
        help="QEMU fault trace limit passed through when fault trace regs are enabled (0 disables limit).",
    )
    ap.add_argument("--qemu-fault-trace-pc", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_PC", ""))
    ap.add_argument("--qemu-fault-trace-pc-lo", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_PC_LO", ""))
    ap.add_argument("--qemu-fault-trace-pc-hi", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_PC_HI", ""))
    ap.add_argument("--qemu-fault-trace-addr", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_ADDR", ""))
    ap.add_argument("--qemu-fault-trace-addr-lo", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_ADDR_LO", ""))
    ap.add_argument("--qemu-fault-trace-addr-hi", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_ADDR_HI", ""))
    ap.add_argument("--qemu-fault-trace-count-lo", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_COUNT_LO", ""))
    ap.add_argument("--qemu-fault-trace-count-hi", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_COUNT_HI", ""))
    ap.add_argument("--qemu-fault-trace-trapnum", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_TRAPNUM", ""))
    ap.add_argument(
        "--qemu-syscall-trace",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_SYSCALL_TRACE", False),
        help="Pass --qemu-syscall-trace to the per-transport runner.",
    )
    ap.add_argument(
        "--qemu-syscall-trace-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_SYSCALL_TRACE_REGS", False),
        help="Pass --qemu-syscall-trace-regs to the per-transport runner.",
    )
    ap.add_argument(
        "--qemu-syscall-trace-strings",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_SYSCALL_TRACE_STRINGS", False),
        help="Pass --qemu-syscall-trace-strings to the per-transport runner.",
    )
    ap.add_argument("--qemu-syscall-trace-nr", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_NR", ""))
    ap.add_argument("--qemu-syscall-trace-limit", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_LIMIT", ""))
    ap.add_argument("--qemu-syscall-trace-pc-lo", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_PC_LO", ""))
    ap.add_argument("--qemu-syscall-trace-pc-hi", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_PC_HI", ""))
    ap.add_argument("--qemu-syscall-trace-string-max", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_STRING_MAX", ""))
    ap.add_argument("--qemu-syscall-trace-dump-args", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_DUMP_ARGS", ""))
    ap.add_argument("--qemu-syscall-trace-dump-arg", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_DUMP_ARG", ""))
    ap.add_argument("--qemu-syscall-trace-dump-bytes", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_DUMP_BYTES", ""))
    ap.add_argument(
        "--qemu-mem-trace",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_MEM_TRACE", False),
        help="Pass --qemu-mem-trace to the per-transport runner.",
    )
    ap.add_argument(
        "--qemu-mem-trace-context",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_MEM_TRACE_CONTEXT", False),
        help="Pass --qemu-mem-trace-context to the per-transport runner.",
    )
    ap.add_argument(
        "--qemu-mem-trace-pre",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_MEM_TRACE_PRE", False),
        help="Pass --qemu-mem-trace-pre to the per-transport runner.",
    )
    ap.add_argument(
        "--qemu-mem-trace-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_MEM_TRACE_REGS", False),
        help="Pass --qemu-mem-trace-regs to the per-transport runner.",
    )
    ap.add_argument("--qemu-mem-trace-addr", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_ADDR", ""))
    ap.add_argument("--qemu-mem-trace-size", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_SIZE", ""))
    ap.add_argument("--qemu-mem-trace-limit", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_LIMIT", ""))
    ap.add_argument("--qemu-mem-trace-access", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_ACCESS", ""))
    ap.add_argument("--qemu-mem-trace-acr", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_ACR", ""))
    ap.add_argument("--qemu-mem-trace-pc", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_PC", ""))
    ap.add_argument("--qemu-mem-trace-pc-lo", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_PC_LO", ""))
    ap.add_argument("--qemu-mem-trace-pc-hi", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_PC_HI", ""))
    ap.add_argument("--qemu-mem-trace-count-lo", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_COUNT_LO", ""))
    ap.add_argument("--qemu-mem-trace-count-hi", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_COUNT_HI", ""))
    ap.add_argument("--qemu-mem-trace-fast", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_FAST", ""))
    ap.add_argument("--qemu-pc-watch", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH", ""))
    ap.add_argument("--qemu-pc-watch-count-lo", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_COUNT_LO", ""))
    ap.add_argument("--qemu-pc-watch-count-hi", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_COUNT_HI", ""))
    ap.add_argument("--qemu-pc-watch-hit-limit", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_HIT_LIMIT", ""))
    ap.add_argument("--qemu-pc-watch-hit-lo", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_HIT_LO", ""))
    ap.add_argument("--qemu-pc-watch-hit-hi", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_HIT_HI", ""))
    ap.add_argument("--qemu-pc-watch-match-gpr", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_MATCH_GPR", ""))
    ap.add_argument("--qemu-pc-watch-match-value", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_MATCH_VALUE", ""))
    ap.add_argument("--qemu-pc-watch-match-mask", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_MATCH_MASK", ""))
    ap.add_argument("--qemu-pc-watch-dump-reg", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_REG", ""))
    ap.add_argument("--qemu-pc-watch-dump-regs", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_REGS", ""))
    ap.add_argument("--qemu-pc-watch-dump-offsets", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_OFFSETS", ""))
    ap.add_argument("--qemu-pc-watch-dump-ptr-offsets", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_PTR_OFFSETS", ""))
    ap.add_argument("--qemu-pc-watch-dump-words", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_WORDS", ""))
    ap.add_argument("--qemu-pc-watch-dump-width", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_WIDTH", ""))
    ap.add_argument("--qemu-pc-watch-dump-code-bytes", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_CODE_BYTES", ""))
    ap.add_argument("--qemu-pc-watch-ring-size", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_RING_SIZE", ""))
    ap.add_argument("--qemu-pc-watch-ring-mem-reg", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_RING_MEM_REG", ""))
    ap.add_argument("--qemu-pc-watch-ring-mem-offset", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_RING_MEM_OFFSET", ""))
    ap.add_argument("--qemu-pc-watch-regs", action="store_true", default=_env_bool("LINX_SPEC_QEMU_PC_WATCH_REGS", False))
    ap.add_argument("--qemu-pc-watch-ring", action="store_true", default=_env_bool("LINX_SPEC_QEMU_PC_WATCH_RING", False))
    ap.add_argument("--qemu-pc-watch-dump-call-ring", action="store_true", default=_env_bool("LINX_SPEC_QEMU_PC_WATCH_DUMP_CALL_RING", False))
    ap.add_argument("--qemu-pc-watch-dump-phys", action="store_true", default=_env_bool("LINX_SPEC_QEMU_PC_WATCH_DUMP_PHYS", False))
    ap.add_argument(
        "--no-progress-timeout",
        type=float,
        default=_env_float("LINX_SPEC_NO_PROGRESS_TIMEOUT", 0.0),
        help="Fail a per-benchmark QEMU run if QEMU emits no output for this many seconds (0 disables).",
    )
    ap.add_argument(
        "--fail-9p-timeout",
        action="store_true",
        default=_env_bool("LINX_SPEC_FAIL_9P_TIMEOUT", False),
        help="Pass --fail-9p-timeout to the per-transport runner for fast 9p gate classification.",
    )
    ap.add_argument(
        "--guest-heartbeat-sec",
        type=int,
        default=_env_int("LINX_SPEC_GUEST_HEARTBEAT_SEC", 0),
        help="Guest child/output heartbeat interval passed through to the initramfs runner (0 disables).",
    )
    ap.add_argument(
        "--guest-proc-diagnostics",
        action="store_true",
        default=_env_bool("LINX_SPEC_GUEST_PROC_DIAGNOSTICS", False),
        help="Pass --guest-proc-diagnostics to enable heavy /proc dumps during guest heartbeat waits.",
    )
    ap.add_argument(
        "--symbolize-heartbeat",
        action="store_true",
        default=_env_bool("LINX_SPEC_SYMBOLIZE_HEARTBEAT", False),
        help="Pass --symbolize-heartbeat to per-transport SPEC runners.",
    )
    ap.add_argument(
        "--append-extra",
        default=os.environ.get("LINX_SPEC_APPEND_EXTRA", ""),
        help="Extra kernel command-line text passed through to the per-transport runner.",
    )
    ap.add_argument(
        "--dump-prefix-bytes",
        type=int,
        default=_env_int("LINX_SPEC_DUMP_PREFIX_BYTES", 0),
        help="Emit first N verified output bytes in initramfs mode (0 disables).",
    )
    ap.add_argument(
        "--out-dir",
        default="",
        help="Output directory for matrix logs/summaries (default: <spec-dir>/tmp/linx-qemu-matrix/stage_<stage>).",
    )
    args = ap.parse_args(argv)

    spec_dir = Path(os.path.expanduser(args.spec_dir)).resolve()
    if not (spec_dir / "benchspec" / "CPU").is_dir():
        raise SystemExit(f"error: invalid SPEC dir: {spec_dir}")
    if not RUNNER.is_file():
        raise SystemExit(f"error: missing runner: {RUNNER}")
    if args.timeout <= 0:
        raise SystemExit("error: --timeout must be > 0")
    if args.memory_mb <= 0:
        raise SystemExit("error: --memory-mb must be > 0")
    if args.heartbeat_sec < 0:
        raise SystemExit("error: --heartbeat-sec must be >= 0")
    if args.qemu_heartbeat_interval < 0:
        raise SystemExit("error: --qemu-heartbeat-interval must be >= 0")
    if args.qemu_heartbeat_code_bytes < 0:
        raise SystemExit("error: --qemu-heartbeat-code-bytes must be >= 0")
    if args.qemu_heartbeat_same_site_warn < 0:
        raise SystemExit("error: --qemu-heartbeat-same-site-warn must be >= 0")
    if args.qemu_fault_trace_limit < 0:
        raise SystemExit("error: --qemu-fault-trace-limit must be >= 0")
    if args.qemu_frame_restore_host_verify_limit < 0:
        raise SystemExit("error: --qemu-frame-restore-host-verify-limit must be >= 0")
    for attr in (
        "qemu_syscall_trace_limit",
        "qemu_syscall_trace_pc_lo",
        "qemu_syscall_trace_pc_hi",
        "qemu_syscall_trace_string_max",
        "qemu_syscall_trace_dump_arg",
        "qemu_syscall_trace_dump_bytes",
        "qemu_mem_trace_addr",
        "qemu_mem_trace_size",
        "qemu_mem_trace_limit",
        "qemu_mem_trace_pc",
        "qemu_mem_trace_pc_lo",
        "qemu_mem_trace_pc_hi",
        "qemu_mem_trace_count_lo",
        "qemu_mem_trace_count_hi",
        "qemu_fret_stk_trace_pc",
        "qemu_fret_stk_trace_pc_lo",
        "qemu_fret_stk_trace_pc_hi",
        "qemu_fret_stk_trace_count_lo",
        "qemu_fret_stk_trace_count_hi",
        "qemu_fret_stk_trace_ra",
        "qemu_fret_stk_trace_limit",
        "qemu_fret_stk_trace_dump_words",
        "qemu_fentry_trace_pc",
        "qemu_fentry_trace_pc_lo",
        "qemu_fentry_trace_pc_hi",
        "qemu_fentry_trace_count_lo",
        "qemu_fentry_trace_count_hi",
        "qemu_fentry_trace_ra",
        "qemu_fentry_trace_sp",
        "qemu_fentry_trace_new_sp",
        "qemu_fentry_trace_limit",
        "qemu_fentry_trace_dump_words",
    ):
        value = str(getattr(args, attr, "") or "").strip()
        if value:
            try:
                parsed = int(value, 0)
            except ValueError as exc:
                raise SystemExit(
                    f"error: --{attr.replace('_', '-')} must be an integer"
                ) from exc
            if parsed < 0:
                raise SystemExit(f"error: --{attr.replace('_', '-')} must be >= 0")
            if attr == "qemu_syscall_trace_dump_arg" and parsed > 5:
                raise SystemExit("error: --qemu-syscall-trace-dump-arg must be <= 5")
    qemu_mem_trace_access = str(getattr(args, "qemu_mem_trace_access", "") or "").strip()
    if qemu_mem_trace_access and qemu_mem_trace_access not in {
        "load",
        "loads",
        "store",
        "stores",
        "all",
        "both",
    }:
        raise SystemExit("error: --qemu-mem-trace-access must be load, store, or all")
    qemu_mem_trace_acr = str(getattr(args, "qemu_mem_trace_acr", "") or "").strip()
    if qemu_mem_trace_acr and qemu_mem_trace_acr not in {"any", "all"}:
        try:
            parsed_acr = int(qemu_mem_trace_acr, 0)
        except ValueError as exc:
            raise SystemExit("error: --qemu-mem-trace-acr must be an integer, any, or all") from exc
        if parsed_acr < 0 or parsed_acr > 15:
            raise SystemExit("error: --qemu-mem-trace-acr must be between 0 and 15")
    for attr in (
        "qemu_pc_watch_hit_limit",
        "qemu_pc_watch_hit_lo",
        "qemu_pc_watch_hit_hi",
        "qemu_pc_watch_dump_words",
        "qemu_pc_watch_dump_width",
        "qemu_pc_watch_dump_code_bytes",
        "qemu_pc_watch_ring_size",
    ):
        value = str(getattr(args, attr, "") or "").strip()
        if value:
            try:
                parsed = int(value, 0)
            except ValueError as exc:
                raise SystemExit(
                    f"error: --{attr.replace('_', '-')} must be an integer"
                ) from exc
            if parsed < 0:
                raise SystemExit(f"error: --{attr.replace('_', '-')} must be >= 0")
    if args.no_progress_timeout < 0:
        raise SystemExit("error: --no-progress-timeout must be >= 0")
    if args.guest_heartbeat_sec < 0:
        raise SystemExit("error: --guest-heartbeat-sec must be >= 0")
    if args.qemu_tlb_fault_trace_limit < 0:
        raise SystemExit("error: --qemu-tlb-fault-trace-limit must be >= 0")
    if args.dump_prefix_bytes < 0:
        raise SystemExit("error: --dump-prefix-bytes must be >= 0")
    qemu_fault_trace_filters = {
        env_name: str(getattr(args, attr, "") or "").strip()
        for attr, env_name in QEMU_FAULT_TRACE_FILTER_ARGS.items()
        if str(getattr(args, attr, "") or "").strip()
    }
    qemu_tlb_fault_trace_filters = {
        env_name: str(getattr(args, attr, "") or "").strip()
        for attr, env_name in QEMU_TLB_FAULT_TRACE_FILTER_ARGS.items()
        if str(getattr(args, attr, "") or "").strip()
    }
    qemu_tlb_fault_trace_requested = bool(
        args.qemu_tlb_fault_trace
        or args.qemu_tlb_fault_trace_limit > 0
        or qemu_tlb_fault_trace_filters
    )
    qemu_pc_watch = {
        env_name: str(getattr(args, attr, "") or "").strip()
        for attr, env_name in QEMU_PC_WATCH_ARGS.items()
        if str(getattr(args, attr, "") or "").strip()
    }
    for attr, env_name in QEMU_PC_WATCH_BOOL_ARGS.items():
        if bool(getattr(args, attr, False)):
            qemu_pc_watch[env_name] = "1"
    qemu_syscall_trace = {
        env_name: str(getattr(args, attr, "") or "").strip()
        for attr, env_name in QEMU_SYSCALL_TRACE_ARGS.items()
        if str(getattr(args, attr, "") or "").strip()
    }
    for attr, env_name in QEMU_SYSCALL_TRACE_BOOL_ARGS.items():
        if bool(getattr(args, attr, False)):
            qemu_syscall_trace[env_name] = "1"
    if bool(getattr(args, "qemu_syscall_trace", False)) or qemu_syscall_trace:
        qemu_syscall_trace["LINX_SYSCALL_TRACE"] = "1"
    qemu_mem_trace = {
        env_name: str(getattr(args, attr, "") or "").strip()
        for attr, env_name in QEMU_MEM_TRACE_ARGS.items()
        if str(getattr(args, attr, "") or "").strip()
    }
    for attr, env_name in QEMU_MEM_TRACE_BOOL_ARGS.items():
        if bool(getattr(args, attr, False)):
            qemu_mem_trace[env_name] = "1"
    if bool(getattr(args, "qemu_mem_trace", False)) or qemu_mem_trace:
        qemu_mem_trace["LINX_MEM_TRACE"] = "1"
    qemu_fret_stk_trace = {
        env_name: str(getattr(args, attr, "") or "").strip()
        for attr, env_name in QEMU_FRET_STK_TRACE_ARGS.items()
        if str(getattr(args, attr, "") or "").strip()
    }
    for attr, env_name in QEMU_FRET_STK_TRACE_BOOL_ARGS.items():
        if bool(getattr(args, attr, False)):
            qemu_fret_stk_trace[env_name] = "1"
    if bool(getattr(args, "qemu_fret_stk_trace", False)) or qemu_fret_stk_trace:
        qemu_fret_stk_trace["LINX_QEMU_FRET_STK_TRACE"] = "1"
    qemu_fentry_trace = {
        env_name: str(getattr(args, attr, "") or "").strip()
        for attr, env_name in QEMU_FENTRY_TRACE_ARGS.items()
        if str(getattr(args, attr, "") or "").strip()
    }
    for attr, env_name in QEMU_FENTRY_TRACE_BOOL_ARGS.items():
        if bool(getattr(args, attr, False)):
            qemu_fentry_trace[env_name] = "1"
    if bool(getattr(args, "qemu_fentry_trace", False)) or qemu_fentry_trace:
        qemu_fentry_trace["LINX_QEMU_FENTRY_TRACE"] = "1"

    transports = _parse_transports(args.transports) if args.transports else _default_transports(args.stage)
    benches = list(args.bench or [])
    if args.out_dir:
        out_dir = Path(os.path.expanduser(args.out_dir)).resolve()
    else:
        out_dir = spec_dir / "tmp" / "linx-qemu-matrix" / f"stage_{args.stage}"
    out_dir.mkdir(parents=True, exist_ok=True)

    started = _utc_now()
    t0 = time.monotonic()

    results: list[dict[str, Any]] = []
    failed_transports: list[str] = []

    for transport in transports:
        transport_out = out_dir / transport
        transport_out.mkdir(parents=True, exist_ok=True)
        log_path = transport_out / f"stage_{args.stage}_{transport}.log"
        runner_summary = transport_out / f"stage_{args.stage}_summary.json"

        cmd = [
            sys.executable,
            str(RUNNER),
            "--spec-dir",
            str(spec_dir),
            "--qemu",
            str(Path(os.path.expanduser(args.qemu)).resolve()),
            "--stage",
            args.stage,
            "--transport",
            transport,
            "--input-set",
            args.input_set,
            "--sysroot",
            str(Path(os.path.expanduser(args.sysroot)).resolve()),
            "--out-dir",
            str(transport_out),
            "--timeout",
            str(args.timeout),
            "--memory-mb",
            str(args.memory_mb),
            "--heartbeat-sec",
            str(args.heartbeat_sec),
            "--qemu-heartbeat-interval",
            str(args.qemu_heartbeat_interval),
            "--qemu-heartbeat-code-bytes",
            str(args.qemu_heartbeat_code_bytes),
            "--qemu-heartbeat-same-site-warn",
            str(args.qemu_heartbeat_same_site_warn),
            "--qemu-fault-trace-limit",
            str(args.qemu_fault_trace_limit),
            "--no-progress-timeout",
            str(args.no_progress_timeout),
            "--guest-heartbeat-sec",
            str(args.guest_heartbeat_sec),
            "--append-extra",
            args.append_extra,
            "--dump-prefix-bytes",
            str(args.dump_prefix_bytes),
        ]
        if args.symbolize_heartbeat:
            cmd.append("--symbolize-heartbeat")
        if args.guest_proc_diagnostics:
            cmd.append("--guest-proc-diagnostics")
        if args.qemu_heartbeat_regs:
            cmd.append("--qemu-heartbeat-regs")
        if args.qemu_frame_stats:
            cmd.append("--qemu-frame-stats")
        if args.qemu_frame_shape_hot:
            cmd.append("--qemu-frame-shape-hot")
        if args.qemu_frame_single_reg_fast:
            cmd.append("--qemu-frame-single-reg-fast")
        if args.qemu_frame_restore_host_load:
            cmd.append("--qemu-frame-restore-host-load")
        if args.qemu_frame_restore_host_verify:
            cmd.append("--qemu-frame-restore-host-verify")
        if args.qemu_frame_restore_host_verify_limit > 0:
            cmd.extend([
                "--qemu-frame-restore-host-verify-limit",
                str(args.qemu_frame_restore_host_verify_limit),
            ])
        if args.qemu_fret_stk_trace:
            cmd.append("--qemu-fret-stk-trace")
        for attr in QEMU_FRET_STK_TRACE_BOOL_ARGS:
            if bool(getattr(args, attr, False)):
                cmd.append("--" + attr.replace("_", "-"))
        for attr in QEMU_FRET_STK_TRACE_ARGS:
            value = str(getattr(args, attr, "") or "").strip()
            if value:
                cmd.extend(["--" + attr.replace("_", "-"), value])
        if args.qemu_fentry_trace:
            cmd.append("--qemu-fentry-trace")
        for attr in QEMU_FENTRY_TRACE_BOOL_ARGS:
            if bool(getattr(args, attr, False)):
                cmd.append("--" + attr.replace("_", "-"))
        for attr in QEMU_FENTRY_TRACE_ARGS:
            value = str(getattr(args, attr, "") or "").strip()
            if value:
                cmd.extend(["--" + attr.replace("_", "-"), value])
        if args.qemu_tlb_stats:
            cmd.append("--qemu-tlb-stats")
        if args.qemu_tlb_inv_hot:
            cmd.append("--qemu-tlb-inv-hot")
        if args.qemu_tlb_fill_stats:
            cmd.append("--qemu-tlb-fill-stats")
        if args.qemu_tlb_fill_hot:
            cmd.append("--qemu-tlb-fill-hot")
        if args.qemu_mmu_cache:
            cmd.append("--qemu-mmu-cache")
        if args.qemu_mmu_cache_stats:
            cmd.append("--qemu-mmu-cache-stats")
        if args.qemu_tlb_fault_trace:
            cmd.append("--qemu-tlb-fault-trace")
        if args.qemu_tlb_fault_trace_limit > 0:
            cmd.extend([
                "--qemu-tlb-fault-trace-limit",
                str(args.qemu_tlb_fault_trace_limit),
            ])
        for attr in QEMU_TLB_FAULT_TRACE_FILTER_ARGS:
            value = str(getattr(args, attr, "") or "").strip()
            if value:
                cmd.extend(["--" + attr.replace("_", "-"), value])
        if args.qemu_tb_stats:
            cmd.append("--qemu-tb-stats")
        if args.qemu_fault_trace:
            cmd.append("--qemu-fault-trace")
        if args.qemu_fault_trace_regs:
            cmd.append("--qemu-fault-trace-regs")
        for attr in QEMU_FAULT_TRACE_FILTER_ARGS:
            value = str(getattr(args, attr, "") or "").strip()
            if value:
                cmd.extend(["--" + attr.replace("_", "-"), value])
        if args.qemu_syscall_trace:
            cmd.append("--qemu-syscall-trace")
        for attr in QEMU_SYSCALL_TRACE_BOOL_ARGS:
            if bool(getattr(args, attr, False)):
                cmd.append("--" + attr.replace("_", "-"))
        for attr in QEMU_SYSCALL_TRACE_ARGS:
            value = str(getattr(args, attr, "") or "").strip()
            if value:
                cmd.extend(["--" + attr.replace("_", "-"), value])
        if args.qemu_mem_trace:
            cmd.append("--qemu-mem-trace")
        for attr in QEMU_MEM_TRACE_BOOL_ARGS:
            if bool(getattr(args, attr, False)):
                cmd.append("--" + attr.replace("_", "-"))
        for attr in QEMU_MEM_TRACE_ARGS:
            value = str(getattr(args, attr, "") or "").strip()
            if value:
                cmd.extend(["--" + attr.replace("_", "-"), value])
        for attr in QEMU_PC_WATCH_ARGS:
            value = str(getattr(args, attr, "") or "").strip()
            if value:
                cmd.extend(["--" + attr.replace("_", "-"), value])
        for attr in QEMU_PC_WATCH_BOOL_ARGS:
            if bool(getattr(args, attr, False)):
                cmd.append("--" + attr.replace("_", "-"))
        if args.fail_9p_timeout:
            cmd.append("--fail-9p-timeout")
        if args.stack_limit.strip():
            cmd.extend(["--stack-limit", args.stack_limit.strip()])
        for bench in benches:
            cmd.extend(["--bench", bench])

        with log_path.open("wb") as log:
            log.write(("$ " + shlex.join(cmd) + "\n").encode("utf-8"))
            log.flush()
            proc = subprocess.run(
                cmd,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )

        summary_obj: dict[str, Any] = {}
        summary_loaded = False
        if runner_summary.is_file():
            try:
                summary_obj = json.loads(runner_summary.read_text(encoding="utf-8"))
                summary_loaded = True
            except json.JSONDecodeError:
                summary_obj = {}

        failed_benches = _transport_failed_benches(summary_obj) if summary_loaded else []
        failure_classes = _transport_failure_classes(summary_obj) if summary_loaded else {}
        failure_details = _transport_failure_details(summary_obj) if summary_loaded else {}
        transport_ok = bool(summary_obj.get("ok", False)) if summary_loaded else False

        row = {
            "transport": transport,
            "command": cmd,
            "returncode": proc.returncode,
            "ok": bool(transport_ok),
            "summary_loaded": summary_loaded,
            "summary_json": str(runner_summary),
            "log": str(log_path),
            "out_dir": str(transport_out),
            "failed_benches": failed_benches,
            "failure_classes": failure_classes,
            "failure_details": failure_details,
        }
        results.append(row)
        if not row["ok"]:
            failed_transports.append(transport)

    overall_ok = len(failed_transports) == 0
    summary = {
        "schema_version": "linx-spec-qemu-matrix-v1",
        "stage": args.stage,
        "input_set": args.input_set,
        "strict": bool(args.strict),
        "spec_dir": str(spec_dir),
        "qemu": str(Path(os.path.expanduser(args.qemu)).resolve()),
        "qemu_provenance": qemu_binary_provenance(
            REPO_ROOT,
            Path(os.path.expanduser(args.qemu)).resolve(),
        ),
        "qemu_machine_extra": os.environ.get("LINX_SPEC_QEMU_MACHINE_EXTRA", "").strip(),
        "qemu_extra_args": _qemu_extra_args(),
        "transports": transports,
        "timeout_sec": int(args.timeout),
        "memory_mb": int(args.memory_mb),
        "stack_limit": args.stack_limit.strip() or "default",
        "heartbeat_sec": float(args.heartbeat_sec),
        "qemu_heartbeat_interval": int(args.qemu_heartbeat_interval),
        "qemu_heartbeat_regs": bool(args.qemu_heartbeat_regs),
        "qemu_heartbeat_code_bytes": int(args.qemu_heartbeat_code_bytes),
        "qemu_heartbeat_same_site_warn": int(args.qemu_heartbeat_same_site_warn),
        "qemu_frame_stats": bool(args.qemu_frame_stats),
        "qemu_frame_shape_hot": bool(args.qemu_frame_shape_hot),
        "qemu_frame_single_reg_fast": bool(args.qemu_frame_single_reg_fast),
        "qemu_frame_restore_host_load": bool(args.qemu_frame_restore_host_load),
        "qemu_frame_restore_host_verify": bool(args.qemu_frame_restore_host_verify),
        "qemu_frame_restore_host_verify_limit": int(args.qemu_frame_restore_host_verify_limit),
        "qemu_fret_stk_trace": qemu_fret_stk_trace,
        "qemu_fentry_trace": qemu_fentry_trace,
        "qemu_tlb_stats": bool(args.qemu_tlb_stats),
        "qemu_tlb_inv_hot": bool(args.qemu_tlb_inv_hot),
        "qemu_tlb_fill_stats": bool(args.qemu_tlb_fill_stats),
        "qemu_tlb_fill_hot": bool(args.qemu_tlb_fill_hot),
        "qemu_mmu_cache": bool(args.qemu_mmu_cache),
        "qemu_mmu_cache_stats": bool(args.qemu_mmu_cache_stats),
        "qemu_tlb_fault_trace": bool(qemu_tlb_fault_trace_requested),
        "qemu_tlb_fault_trace_limit": int(args.qemu_tlb_fault_trace_limit),
        "qemu_tlb_fault_trace_filters": qemu_tlb_fault_trace_filters,
        "qemu_tb_stats": bool(args.qemu_tb_stats),
        "qemu_fault_trace": bool(args.qemu_fault_trace or qemu_fault_trace_filters),
        "qemu_fault_trace_regs": bool(args.qemu_fault_trace_regs),
        "qemu_fault_trace_limit": int(args.qemu_fault_trace_limit),
        "qemu_fault_trace_filters": qemu_fault_trace_filters,
        "qemu_pc_watch": qemu_pc_watch,
        "qemu_syscall_trace": qemu_syscall_trace,
        "qemu_mem_trace": qemu_mem_trace,
        "no_progress_timeout": float(args.no_progress_timeout),
        "fail_9p_timeout": bool(args.fail_9p_timeout),
        "guest_heartbeat_sec": int(args.guest_heartbeat_sec),
        "guest_proc_diagnostics": bool(args.guest_proc_diagnostics),
        "symbolize_heartbeat": bool(args.symbolize_heartbeat),
        "append_extra": str(args.append_extra),
        "dump_prefix_bytes": int(args.dump_prefix_bytes),
        "bench_override": benches,
        "started_at_utc": started,
        "finished_at_utc": _utc_now(),
        "elapsed_sec": round(time.monotonic() - t0, 3),
        "ok": overall_ok,
        "failed_transports": failed_transports,
        "results": results,
    }

    summary_json = out_dir / "qemu_matrix_summary.json"
    summary_md = out_dir / "qemu_matrix_summary.md"
    summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_md(summary_md, summary)

    print(f"summary_json={summary_json}")
    print(f"summary_md={summary_md}")
    print(f"ok={str(overall_ok).lower()} strict={int(bool(args.strict))}")

    if args.strict and not overall_ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
