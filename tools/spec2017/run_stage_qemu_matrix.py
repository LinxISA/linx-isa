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
            "heartbeat_tb_stats": failed_run.get("heartbeat_tb_stats") or {},
            "heartbeat_tlb_fill_hot": failed_run.get("heartbeat_tlb_fill_hot") or {},
            "bstart_cache_stats": failed_run.get("bstart_cache_stats") or {},
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
        fcmp = ""
        if row.get("fcmp_trace_seen"):
            fcmp = f" fcmp-trace={row.get('fcmp_trace_count')}"
        tlbfill = ""
        if row.get("tlb_fill_trace_seen"):
            tlbfill = f" tlbfill-trace={row.get('tlb_fill_trace_count')}"
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
        mmu_cache = _format_mmu_cache_stats(row)
        frame_stats = _format_frame_stats(row)
        tb_stats = _format_tb_stats(row)
        bstart_cache = _format_bstart_cache_stats(row)
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
            f"bpc={bpc}{kernel}{hb_stall}{fcmp}{tlbfill}{tlbfill_stats}{tlbfill_hot}{mmu_cache}{frame_stats}{tb_stats}{bstart_cache}{mprotect}"
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
    lines.append(f"- qemu_tb_stats: `{str(bool(summary.get('qemu_tb_stats', False))).lower()}`")
    lines.append(f"- qemu_fault_trace: `{str(bool(summary.get('qemu_fault_trace', False))).lower()}`")
    lines.append(f"- qemu_fault_trace_regs: `{str(bool(summary.get('qemu_fault_trace_regs', False))).lower()}`")
    lines.append(f"- qemu_fault_trace_limit: `{summary.get('qemu_fault_trace_limit', 1)}`")
    filters = summary.get("qemu_fault_trace_filters") or {}
    if filters:
        filter_text = ", ".join(f"{k}={v}" for k, v in sorted(filters.items()))
        lines.append(f"- qemu_fault_trace_filters: `{filter_text}`")
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
    if args.no_progress_timeout < 0:
        raise SystemExit("error: --no-progress-timeout must be >= 0")
    if args.guest_heartbeat_sec < 0:
        raise SystemExit("error: --guest-heartbeat-sec must be >= 0")
    if args.dump_prefix_bytes < 0:
        raise SystemExit("error: --dump-prefix-bytes must be >= 0")
    qemu_fault_trace_filters = {
        env_name: str(getattr(args, attr, "") or "").strip()
        for attr, env_name in QEMU_FAULT_TRACE_FILTER_ARGS.items()
        if str(getattr(args, attr, "") or "").strip()
    }

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
        "qemu_tb_stats": bool(args.qemu_tb_stats),
        "qemu_fault_trace": bool(args.qemu_fault_trace or qemu_fault_trace_filters),
        "qemu_fault_trace_regs": bool(args.qemu_fault_trace_regs),
        "qemu_fault_trace_limit": int(args.qemu_fault_trace_limit),
        "qemu_fault_trace_filters": qemu_fault_trace_filters,
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
