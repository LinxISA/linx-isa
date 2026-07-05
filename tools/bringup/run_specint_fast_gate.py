#!/usr/bin/env python3
"""Run the fast SPECint QEMU gate over test/train input sets.

The private SPEC corpus and low-level SPEC runner live under ignored paths.
This tracked wrapper keeps the public gate policy stable: small test/train
suites first, expensive promotion work only in the nightly profile. Large
payload rows that do not fit the initramfs path are split into transport
specific shards unless --transports explicitly overrides the policy.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from qemu_build_paths import default_qemu_binary, qemu_binary_provenance


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPEC_DIR = REPO_ROOT / "workloads" / "spec2017" / "cpu2017v118_x64_gcc12_avx2"
DEFAULT_RUNNER = REPO_ROOT / "tools" / "spec2017" / "run_stage_qemu_matrix.py"


@dataclass(frozen=True)
class Suite:
    name: str
    stage: str
    input_set: str
    benches: tuple[str, ...]
    transports: str
    timeout_env: str
    timeout_default: int
    description: str


SPECINT_STAGE_B_BENCHES = (
    "500.perlbench_r",
    "502.gcc_r",
    "505.mcf_r",
    "520.omnetpp_r",
    "523.xalancbmk_r",
    "525.x264_r",
    "531.deepsjeng_r",
    "541.leela_r",
    "557.xz_r",
    "999.specrand_ir",
)

SPECINT_TRAIN_PROMOTION_BENCHES = tuple(
    bench
    for bench in SPECINT_STAGE_B_BENCHES
    if bench not in {"505.mcf_r", "531.deepsjeng_r", "999.specrand_ir"}
)

LARGE_PAYLOAD_TRANSPORTS: dict[str, str] = {
    "525.x264_r": "9p",
}


SUITES: dict[str, Suite] = {
    "test-smoke": Suite(
        name="test-smoke",
        stage="a",
        input_set="test",
        benches=("999.specrand_ir",),
        transports="initramfs",
        timeout_env="SPECINT_TEST_SMOKE_TIMEOUT",
        timeout_default=180,
        description="fast test-input sentinel without refrate cost",
    ),
    "train-smoke": Suite(
        name="train-smoke",
        stage="a",
        input_set="train",
        benches=("999.specrand_ir",),
        transports="initramfs",
        timeout_env="SPECINT_TRAIN_SMOKE_TIMEOUT",
        timeout_default=300,
        description="fast train-input sentinel without refrate cost",
    ),
    "train-cpu-stress": Suite(
        name="train-cpu-stress",
        stage="a",
        input_set="train",
        benches=("531.deepsjeng_r",),
        transports="initramfs",
        timeout_env="SPECINT_TRAIN_CPU_STRESS_TIMEOUT",
        timeout_default=900,
        description="isolated train-input CPU/control-flow stress check",
    ),
    "test-cpu-stress": Suite(
        name="test-cpu-stress",
        stage="a",
        input_set="test",
        benches=("531.deepsjeng_r",),
        transports="initramfs",
        timeout_env="SPECINT_TEST_CPU_STRESS_TIMEOUT",
        timeout_default=900,
        description="isolated test-input CPU/control-flow stress check",
    ),
    "test-vm-stress": Suite(
        name="test-vm-stress",
        stage="a",
        input_set="test",
        benches=("505.mcf_r",),
        transports="initramfs",
        timeout_env="SPECINT_TEST_VM_STRESS_TIMEOUT",
        timeout_default=900,
        description="isolated mcf VM/allocation stress check",
    ),
    "train-vm-stress": Suite(
        name="train-vm-stress",
        stage="a",
        input_set="train",
        benches=("505.mcf_r",),
        transports="initramfs",
        timeout_env="SPECINT_TRAIN_VM_STRESS_TIMEOUT",
        timeout_default=1200,
        description="train-input mcf VM/allocation stress check",
    ),
    "test-all": Suite(
        name="test-all",
        stage="b",
        input_set="test",
        benches=SPECINT_STAGE_B_BENCHES,
        transports="initramfs",
        timeout_env="SPECINT_TEST_ALL_TIMEOUT",
        timeout_default=120,
        description="bounded all-SPECint test-input diagnostic gate",
    ),
    "train-promotion": Suite(
        name="train-promotion",
        stage="b",
        input_set="train",
        benches=SPECINT_TRAIN_PROMOTION_BENCHES,
        transports="initramfs",
        timeout_env="SPECINT_TRAIN_PROMOTION_TIMEOUT",
        timeout_default=1800,
        description="nightly train-input SPECint promotion breadth",
    ),
    "train-all": Suite(
        name="train-all",
        stage="b",
        input_set="train",
        benches=SPECINT_STAGE_B_BENCHES,
        transports="initramfs",
        timeout_env="SPECINT_TRAIN_ALL_TIMEOUT",
        timeout_default=180,
        description="bounded all-SPECint train-input diagnostic gate",
    ),
}

PROFILE_SUITES: dict[str, tuple[str, ...]] = {
    "smoke": ("test-smoke",),
    "pr": ("test-smoke", "train-smoke"),
    "test": ("test-all",),
    "train": ("train-all",),
    "test-train": ("test-all", "train-all"),
    "nightly": (
        "test-smoke",
        "train-smoke",
        "test-cpu-stress",
        "test-vm-stress",
        "train-cpu-stress",
        "train-vm-stress",
        "train-promotion",
    ),
}


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


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


def _default_qemu() -> str:
    env = os.environ.get("QEMU", "").strip()
    if env:
        return str(Path(os.path.expanduser(env)).resolve())
    qemu = default_qemu_binary(REPO_ROOT)
    return str(qemu.resolve())


def _qemu_extra_args() -> list[str]:
    return shlex.split(os.environ.get("LINX_SPEC_QEMU_EXTRA_ARGS", ""))


def _runner_supports_option(runner: Path, option: str) -> bool:
    try:
        return option in runner.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False


def _select_suites(profile: str, requested: list[str]) -> list[Suite]:
    names = list(PROFILE_SUITES[profile])
    if requested:
        wanted = set(requested)
        unknown = sorted(wanted - set(SUITES))
        if unknown:
            raise SystemExit(f"error: unknown suite(s): {', '.join(unknown)}")
        names = [name for name in names if name in wanted]
        missing = sorted(wanted - set(names))
        if missing:
            raise SystemExit(
                f"error: suite(s) not enabled by profile {profile}: {', '.join(missing)}"
            )
    return [SUITES[name] for name in names]


def _suite_execution_units(suite: Suite, transports_override: str) -> list[Suite]:
    override = transports_override.strip()
    if override:
        return [replace(suite, transports=override)]

    large_benches = tuple(
        bench for bench in suite.benches if bench in LARGE_PAYLOAD_TRANSPORTS
    )
    if not large_benches or suite.transports != "initramfs":
        return [suite]

    normal_benches = tuple(
        bench for bench in suite.benches if bench not in LARGE_PAYLOAD_TRANSPORTS
    )
    units: list[Suite] = []
    if normal_benches:
        units.append(replace(suite, benches=normal_benches))

    by_transport: dict[str, list[str]] = {}
    for bench in large_benches:
        by_transport.setdefault(LARGE_PAYLOAD_TRANSPORTS[bench], []).append(bench)

    for transport, benches in sorted(by_transport.items()):
        suffix = transport.replace(",", "-").replace("/", "-")
        units.append(
            replace(
                suite,
                name=f"{suite.name}-large-{suffix}",
                benches=tuple(benches),
                transports=transport,
                description=f"{suite.description}; large payload via {transport}",
            )
        )
    return units


def _read_matrix_summary(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"loaded": False, "ok": False, "error": f"missing {path}"}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"loaded": False, "ok": False, "error": str(exc)}
    obj["loaded"] = True
    return obj


def _matrix_failure_classes(matrix: dict[str, Any]) -> dict[str, str]:
    classes: dict[str, str] = {}
    results = matrix.get("results", [])
    if not isinstance(results, list):
        return classes
    for row in results:
        if not isinstance(row, dict):
            continue
        row_classes = row.get("failure_classes", {})
        if not isinstance(row_classes, dict):
            continue
        for bench, cls in row_classes.items():
            classes[str(bench)] = str(cls)
    return classes


def _matrix_failure_details(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    details: dict[str, dict[str, Any]] = {}
    results = matrix.get("results", [])
    if not isinstance(results, list):
        return details
    for row in results:
        if not isinstance(row, dict):
            continue
        row_details = row.get("failure_details", {})
        if not isinstance(row_details, dict):
            continue
        for bench, detail in row_details.items():
            if isinstance(detail, dict):
                details[str(bench)] = detail
    return details


def _format_failure_details(details: dict[str, dict[str, Any]]) -> str:
    if not details:
        return "-"
    parts: list[str] = []
    for bench, row in sorted(details.items()):
        running = "running" if row.get("heartbeat_running") else "not-running"
        site = "site-progress" if row.get("heartbeat_site_progress") else "same-site"
        bpc = row.get("heartbeat_last_bpc") or "no-bpc"
        progress = row.get("heartbeat_last_progress") or "no-progress-tag"
        hb_stall = ""
        if row.get("heartbeat_stall_seen"):
            hb_stall = (
                " heartbeat-stall="
                f"{row.get('heartbeat_stall_status') or 'same-site'}:"
                f"{row.get('heartbeat_stall_repeats')}/"
                f"{row.get('heartbeat_stall_threshold')}"
            )
        tlbfill = ""
        if row.get("tlb_fill_trace_seen"):
            tlbfill = f" tlbfill-trace={row.get('tlb_fill_trace_count')}"
        if row.get("tlb_fault_trace_seen"):
            tlbfill += f" tlbfault-trace={row.get('tlb_fault_trace_count')}"
        heartbeat_tlb_fill = row.get("heartbeat_tlb_fill")
        if isinstance(heartbeat_tlb_fill, dict) and heartbeat_tlb_fill.get("total") is not None:
            tlbfill += (
                f" tlbf={heartbeat_tlb_fill.get('total')}"
                f"/f{heartbeat_tlb_fill.get('fetch')}"
                f"/l{heartbeat_tlb_fill.get('load')}"
                f"/s{heartbeat_tlb_fill.get('store')}"
                f"/p{heartbeat_tlb_fill.get('probe')}"
            )
            if heartbeat_tlb_fill.get("user") is not None:
                tlbfill += (
                    f"/u{heartbeat_tlb_fill.get('user')}"
                    f"/k{heartbeat_tlb_fill.get('kernel')}"
                    f"/o{heartbeat_tlb_fill.get('other')}"
                )
        heartbeat_tlb_fill_hot = row.get("heartbeat_tlb_fill_hot")
        if (
            isinstance(heartbeat_tlb_fill_hot, dict)
            and heartbeat_tlb_fill_hot.get("seen")
            and heartbeat_tlb_fill_hot.get("top0_count") is not None
        ):
            tlbfill += (
                f" tlbf-hot={heartbeat_tlb_fill_hot.get('top0_count')}"
                f"@{heartbeat_tlb_fill_hot.get('top0_page') or 'no-page'}"
                f"/a{heartbeat_tlb_fill_hot.get('top0_access')}"
                f"/m{heartbeat_tlb_fill_hot.get('top0_mmu')}"
                f" evict={heartbeat_tlb_fill_hot.get('evictions')}"
            )
        heartbeat_tlb_inv_hot = row.get("heartbeat_tlb_inv_hot")
        if (
            isinstance(heartbeat_tlb_inv_hot, dict)
            and heartbeat_tlb_inv_hot.get("seen")
            and heartbeat_tlb_inv_hot.get("top0_count") is not None
        ):
            top0_count = heartbeat_tlb_inv_hot.get("max_delta_top0_count")
            if top0_count is None:
                top0_count = heartbeat_tlb_inv_hot.get("top0_count")
            top0_delta = heartbeat_tlb_inv_hot.get("max_delta_top0_delta")
            if top0_delta is None:
                top0_delta = heartbeat_tlb_inv_hot.get("top0_delta")
            count_tag = f"{top0_delta}/{top0_count}" if top0_delta is not None else str(top0_count)
            top0_op = heartbeat_tlb_inv_hot.get("max_delta_top0_op") or heartbeat_tlb_inv_hot.get("top0_op") or "op"
            top0_pc = heartbeat_tlb_inv_hot.get("max_delta_top0_pc") or heartbeat_tlb_inv_hot.get("top0_pc") or "no-pc"
            top0_page = heartbeat_tlb_inv_hot.get("max_delta_top0_page") or heartbeat_tlb_inv_hot.get("top0_page") or "no-page"
            tlbfill += (
                f" tlbi-hot={count_tag}"
                f":{top0_op}"
                f"@{top0_pc}"
                f"/page{top0_page}"
                f" evict={heartbeat_tlb_inv_hot.get('evictions')}"
            )
        heartbeat_tlb_invalidation = row.get("heartbeat_tlb_invalidation")
        tlbinv = ""
        if isinstance(heartbeat_tlb_invalidation, dict) and heartbeat_tlb_invalidation.get("iv") is not None:
            last_bpc = heartbeat_tlb_invalidation.get("last_bpc")
            last_operand = heartbeat_tlb_invalidation.get("last_operand")
            last = ""
            if last_bpc or last_operand:
                last = f" last={last_bpc or 'no-bpc'}@{last_operand or 'no-op'}"
            tlbinv = (
                f" tlbi=iv{heartbeat_tlb_invalidation.get('iv')}"
                f"/iav{heartbeat_tlb_invalidation.get('iav')}"
                f"/ia{heartbeat_tlb_invalidation.get('ia')}"
                f"/iall{heartbeat_tlb_invalidation.get('iall')}"
                f"{last}"
            )
        bstart_cache = ""
        bstart_cache_stats = row.get("bstart_cache_stats")
        if isinstance(bstart_cache_stats, dict) and bstart_cache_stats.get("seen"):
            bstart_cache = (
                f" bstart-cache={bstart_cache_stats.get('hits')}/"
                f"{bstart_cache_stats.get('checks')}"
                f" hit={bstart_cache_stats.get('hit_pct')}%"
                f" miss={bstart_cache_stats.get('bstarts')}"
                f" reset={bstart_cache_stats.get('resets')}/"
                f"{bstart_cache_stats.get('page_resets')}"
            )
        pc_watch = ""
        pc_watch_stats = row.get("pc_watch")
        if isinstance(pc_watch_stats, dict) and pc_watch_stats.get("seen"):
            pc_watch = f" pc-watch={pc_watch_stats.get('line_count')}"
            if pc_watch_stats.get("ring_seen"):
                pc_watch += (
                    f"/ring{pc_watch_stats.get('ring_count')}"
                    f"/entries{pc_watch_stats.get('ring_entry_count')}"
                )
            last_entry = pc_watch_stats.get("last_ring_entry_fields")
            if isinstance(last_entry, dict) and last_entry.get("mem_ok") is not None:
                pc_watch += (
                    f"/mem{last_entry.get('mem_ok')}"
                    f"@{last_entry.get('mem_addr') or 'no-addr'}"
                    f"={last_entry.get('mem_value') or 'no-value'}"
                )
        mprotect = ""
        if row.get("mprotect_trace_seen"):
            mprotect = f" mprotect-trace={row.get('mprotect_trace_count')}"
        parts.append(f"{bench}: {running}/{site} {progress} bpc={bpc}{hb_stall}{tlbfill}{tlbinv}{bstart_cache}{pc_watch}{mprotect}")
    return ", ".join(parts)


def _suite_command(
    *,
    suite: Suite,
    runner: Path,
    spec_dir: Path,
    qemu: Path,
    sysroot: Path,
    out_dir: Path,
    append_extra: str,
    heartbeat_sec: float,
    memory_mb: int,
    qemu_heartbeat_interval: int,
    qemu_heartbeat_regs: bool,
    qemu_heartbeat_code_bytes: int,
    qemu_heartbeat_same_site_warn: int,
    qemu_frame_stats: bool,
    qemu_frame_shape_hot: bool,
    qemu_frame_single_reg_fast: bool,
    qemu_frame_restore_host_load: bool,
    qemu_tlb_stats: bool,
    qemu_tlb_inv_hot: bool,
    qemu_tlb_fill_stats: bool,
    qemu_tlb_fill_hot: bool,
    qemu_mmu_cache: bool,
    qemu_mmu_cache_stats: bool,
    qemu_tlb_fault_trace: bool,
    qemu_tlb_fault_trace_limit: int,
    qemu_tlb_fault_trace_addr: str,
    qemu_tlb_fault_trace_addr_lo: str,
    qemu_tlb_fault_trace_addr_hi: str,
    qemu_tlb_fault_trace_count_lo: str,
    qemu_tlb_fault_trace_count_hi: str,
    qemu_tb_stats: bool,
    no_progress_timeout: float,
    forward_memory_mb: bool,
    forward_qemu_heartbeat: bool,
    forward_qemu_heartbeat_regs: bool,
    forward_qemu_heartbeat_code_bytes: bool,
    forward_qemu_heartbeat_same_site_warn: bool,
    forward_qemu_frame_stats: bool,
    forward_qemu_frame_shape_hot: bool,
    forward_qemu_frame_single_reg_fast: bool,
    forward_qemu_frame_restore_host_load: bool,
    forward_qemu_tlb_stats: bool,
    forward_qemu_tlb_inv_hot: bool,
    forward_qemu_tlb_fill_stats: bool,
    forward_qemu_tlb_fill_hot: bool,
    forward_qemu_mmu_cache: bool,
    forward_qemu_mmu_cache_stats: bool,
    forward_qemu_tlb_fault_trace: bool,
    forward_qemu_tb_stats: bool,
    forward_no_progress: bool,
    forward_stack_limit: bool,
    forward_symbolize_heartbeat: bool,
    stack_limit: str,
    symbolize_heartbeat: bool,
    guest_heartbeat_sec: int,
    dump_prefix_bytes: int,
    fail_9p_timeout: bool,
) -> list[str]:
    timeout = _env_int(suite.timeout_env, suite.timeout_default)
    cmd = [
        sys.executable,
        str(runner),
        "--spec-dir",
        str(spec_dir),
        "--qemu",
        str(qemu),
        "--stage",
        suite.stage,
        "--input-set",
        suite.input_set,
        "--transports",
        suite.transports,
        "--sysroot",
        str(sysroot),
        "--timeout",
        str(timeout),
        "--heartbeat-sec",
        str(heartbeat_sec),
        "--guest-heartbeat-sec",
        str(guest_heartbeat_sec),
        "--append-extra",
        append_extra,
        "--dump-prefix-bytes",
        str(dump_prefix_bytes),
        "--strict",
        "--out-dir",
        str(out_dir / suite.name),
    ]
    if forward_memory_mb:
        cmd.extend(["--memory-mb", str(memory_mb)])
    if forward_qemu_heartbeat:
        cmd.extend(["--qemu-heartbeat-interval", str(qemu_heartbeat_interval)])
    if qemu_heartbeat_regs and forward_qemu_heartbeat_regs:
        cmd.append("--qemu-heartbeat-regs")
    if qemu_heartbeat_code_bytes and forward_qemu_heartbeat_code_bytes:
        cmd.extend(["--qemu-heartbeat-code-bytes", str(qemu_heartbeat_code_bytes)])
    if qemu_heartbeat_same_site_warn and forward_qemu_heartbeat_same_site_warn:
        cmd.extend(["--qemu-heartbeat-same-site-warn", str(qemu_heartbeat_same_site_warn)])
    if qemu_frame_stats and forward_qemu_frame_stats:
        cmd.append("--qemu-frame-stats")
    if qemu_frame_shape_hot and forward_qemu_frame_shape_hot:
        cmd.append("--qemu-frame-shape-hot")
    if qemu_frame_single_reg_fast and forward_qemu_frame_single_reg_fast:
        cmd.append("--qemu-frame-single-reg-fast")
    if qemu_frame_restore_host_load and forward_qemu_frame_restore_host_load:
        cmd.append("--qemu-frame-restore-host-load")
    if qemu_tlb_stats and forward_qemu_tlb_stats:
        cmd.append("--qemu-tlb-stats")
    if qemu_tlb_inv_hot and forward_qemu_tlb_inv_hot:
        cmd.append("--qemu-tlb-inv-hot")
    if qemu_tlb_fill_stats and forward_qemu_tlb_fill_stats:
        cmd.append("--qemu-tlb-fill-stats")
    if qemu_tlb_fill_hot and forward_qemu_tlb_fill_hot:
        cmd.append("--qemu-tlb-fill-hot")
    if qemu_mmu_cache and forward_qemu_mmu_cache:
        cmd.append("--qemu-mmu-cache")
    if qemu_mmu_cache_stats and forward_qemu_mmu_cache_stats:
        cmd.append("--qemu-mmu-cache-stats")
    if qemu_tlb_fault_trace and forward_qemu_tlb_fault_trace:
        cmd.append("--qemu-tlb-fault-trace")
    if (
        qemu_tlb_fault_trace_limit > 0
        and forward_qemu_tlb_fault_trace
    ):
        cmd.extend(["--qemu-tlb-fault-trace-limit", str(qemu_tlb_fault_trace_limit)])
    if forward_qemu_tlb_fault_trace:
        for opt, value in (
            ("--qemu-tlb-fault-trace-addr", qemu_tlb_fault_trace_addr),
            ("--qemu-tlb-fault-trace-addr-lo", qemu_tlb_fault_trace_addr_lo),
            ("--qemu-tlb-fault-trace-addr-hi", qemu_tlb_fault_trace_addr_hi),
            ("--qemu-tlb-fault-trace-count-lo", qemu_tlb_fault_trace_count_lo),
            ("--qemu-tlb-fault-trace-count-hi", qemu_tlb_fault_trace_count_hi),
        ):
            if value.strip():
                cmd.extend([opt, value.strip()])
    if qemu_tb_stats and forward_qemu_tb_stats:
        cmd.append("--qemu-tb-stats")
    if forward_no_progress:
        cmd.extend(["--no-progress-timeout", str(no_progress_timeout)])
    if stack_limit.strip() and forward_stack_limit:
        cmd.extend(["--stack-limit", stack_limit.strip()])
    if symbolize_heartbeat and forward_symbolize_heartbeat:
        cmd.append("--symbolize-heartbeat")
    if fail_9p_timeout:
        cmd.append("--fail-9p-timeout")
    for bench in suite.benches:
        cmd.extend(["--bench", bench])
    return cmd


def _auto_fail_9p_timeout(unit: Suite, transports_override: str) -> bool:
    if transports_override.strip():
        return False
    transports = {item.strip() for item in unit.transports.split(",") if item.strip()}
    return unit.name.endswith("-large-9p") and "9p" in transports


def _format_filter_dict(filters: dict[str, Any]) -> str:
    if not filters:
        return "-"
    return " ".join(f"{key}={shlex.quote(str(value))}" for key, value in sorted(filters.items()))


def _write_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# SPECint Fast Gate Summary",
        "",
        "## Run",
        "",
        f"- profile: `{summary['profile']}`",
        f"- ok: `{str(summary['ok']).lower()}`",
        f"- elapsed_sec: `{summary['elapsed_sec']}`",
        f"- qemu: `{summary['qemu']}`",
        f"- qemu_version: `{(summary.get('qemu_provenance') or {}).get('version', '-')}`",
        f"- qemu_repo_head: `{(summary.get('qemu_provenance') or {}).get('qemu_repo_head', '-')}`",
        "- qemu_clean_build_for_head: "
        f"`{str(bool((summary.get('qemu_provenance') or {}).get('clean_build_for_head', False))).lower()}`",
        f"- qemu_machine_extra: `{summary.get('qemu_machine_extra') or '-'}`",
        "- qemu_extra_args: "
        f"`{shlex.join([str(arg) for arg in summary.get('qemu_extra_args') or []]) or '-'}`",
        f"- spec_dir: `{summary['spec_dir']}`",
        f"- memory_mb: `{summary['memory_mb']}`",
        f"- stack_limit: `{summary['stack_limit']}`",
        f"- qemu_heartbeat_interval: `{summary['qemu_heartbeat_interval']}`",
        f"- qemu_heartbeat_regs: `{str(bool(summary.get('qemu_heartbeat_regs', False))).lower()}`",
        f"- qemu_heartbeat_code_bytes: `{summary.get('qemu_heartbeat_code_bytes', 0)}`",
        f"- qemu_heartbeat_same_site_warn: `{summary.get('qemu_heartbeat_same_site_warn', 0)}`",
        f"- qemu_frame_stats: `{str(bool(summary.get('qemu_frame_stats', False))).lower()}`",
        f"- qemu_frame_shape_hot: `{str(bool(summary.get('qemu_frame_shape_hot', False))).lower()}`",
        f"- qemu_frame_single_reg_fast: `{str(bool(summary.get('qemu_frame_single_reg_fast', False))).lower()}`",
        "- qemu_frame_restore_host_load: "
        f"`{str(bool(summary.get('qemu_frame_restore_host_load', False))).lower()}`",
        f"- qemu_tlb_stats: `{str(bool(summary.get('qemu_tlb_stats', False))).lower()}`",
        f"- qemu_tlb_inv_hot: `{str(bool(summary.get('qemu_tlb_inv_hot', False))).lower()}`",
        f"- qemu_tlb_fill_stats: `{str(bool(summary.get('qemu_tlb_fill_stats', False))).lower()}`",
        f"- qemu_tlb_fill_hot: `{str(bool(summary.get('qemu_tlb_fill_hot', False))).lower()}`",
        f"- qemu_mmu_cache: `{str(bool(summary.get('qemu_mmu_cache', False))).lower()}`",
        f"- qemu_mmu_cache_stats: `{str(bool(summary.get('qemu_mmu_cache_stats', False))).lower()}`",
        f"- qemu_tlb_fault_trace: `{str(bool(summary.get('qemu_tlb_fault_trace', False))).lower()}`",
        f"- qemu_tlb_fault_trace_limit: `{summary.get('qemu_tlb_fault_trace_limit', 0)}`",
        f"- qemu_tlb_fault_trace_filters: `{_format_filter_dict(summary.get('qemu_tlb_fault_trace_filters') or {})}`",
        f"- qemu_tb_stats: `{str(bool(summary.get('qemu_tb_stats', False))).lower()}`",
        f"- fail_9p_timeout: `{str(bool(summary.get('fail_9p_timeout', False))).lower()}`",
        "",
        "## Suites",
        "",
        "| Suite | Input | Benches | OK | Return | Elapsed | Failure Classes | Liveness | Summary |",
        "|---|---|---|---:|---:|---:|---|---|---|",
    ]
    for row in summary["suites"]:
        benches = ", ".join(row["benches"])
        failure_classes = row.get("failure_classes", {})
        if isinstance(failure_classes, dict) and failure_classes:
            classes_text = ", ".join(
                f"{bench}: {cls}" for bench, cls in sorted(failure_classes.items())
            )
        else:
            classes_text = "-"
        failure_details = row.get("failure_details", {})
        details_text = _format_failure_details(
            failure_details if isinstance(failure_details, dict) else {}
        )
        lines.append(
            "| "
            f"`{row['name']}` | "
            f"`{row['input_set']}` | "
            f"`{benches}` | "
            f"`{str(row['ok']).lower()}` | "
            f"`{row['returncode']}` | "
            f"`{row['elapsed_sec']}` | "
            f"`{classes_text}` | "
            f"`{details_text}` | "
            f"`{row['matrix_summary']}` |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=sorted(PROFILE_SUITES), default="pr")
    parser.add_argument("--suite", action="append", default=[], help="Run only a named suite enabled by --profile.")
    parser.add_argument("--spec-dir", default=str(DEFAULT_SPEC_DIR))
    parser.add_argument("--runner", default=str(DEFAULT_RUNNER))
    parser.add_argument("--qemu", default=_default_qemu())
    parser.add_argument("--sysroot", default=str(REPO_ROOT / "out" / "libc" / "musl" / "install" / "phase-b"))
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "workloads" / "generated" / "specint-fast-gate"))
    parser.add_argument("--append-extra", default=os.environ.get("SPEC_APPEND_EXTRA", os.environ.get("LINX_SPEC_APPEND_EXTRA", "norandmaps")))
    parser.add_argument("--heartbeat-sec", type=float, default=float(os.environ.get("SPEC_HEARTBEAT_SEC", os.environ.get("LINX_SPEC_HEARTBEAT_SEC", "30"))))
    parser.add_argument("--memory-mb", type=int, default=_env_int("SPEC_MEMORY_MB", _env_int("LINX_SPEC_MEMORY_MB", 2048)))
    parser.add_argument("--qemu-heartbeat-interval", type=int, default=_env_int("SPEC_QEMU_HEARTBEAT_INTERVAL", _env_int("LINX_SPEC_QEMU_HEARTBEAT_INTERVAL", 0)))
    parser.add_argument("--qemu-heartbeat-regs", action="store_true", default=_env_bool("SPEC_QEMU_HEARTBEAT_REGS", _env_bool("LINX_SPEC_QEMU_HEARTBEAT_REGS", False)))
    parser.add_argument("--qemu-heartbeat-code-bytes", type=int, default=_env_int("SPEC_QEMU_HEARTBEAT_CODE_BYTES", _env_int("LINX_SPEC_QEMU_HEARTBEAT_CODE_BYTES", 0)))
    parser.add_argument("--qemu-heartbeat-same-site-warn", type=int, default=_env_int("SPEC_QEMU_HEARTBEAT_SAME_SITE_WARN", _env_int("LINX_SPEC_QEMU_HEARTBEAT_SAME_SITE_WARN", 0)))
    parser.add_argument("--qemu-frame-stats", action="store_true", default=_env_bool("SPEC_QEMU_FRAME_STATS", _env_bool("LINX_SPEC_QEMU_FRAME_STATS", False)))
    parser.add_argument(
        "--qemu-frame-shape-hot",
        action="store_true",
        default=_env_bool(
            "SPEC_QEMU_FRAME_SHAPE_HOT",
            _env_bool("LINX_SPEC_QEMU_FRAME_SHAPE_HOT", False),
        ),
        help="Forward QEMU's opt-in frame-template shape hot-site heartbeat sketch.",
    )
    parser.add_argument(
        "--qemu-frame-single-reg-fast",
        action="store_true",
        default=_env_bool(
            "SPEC_QEMU_FRAME_SINGLE_REG_FAST",
            _env_bool("LINX_SPEC_QEMU_FRAME_SINGLE_REG_FAST", False),
        ),
        help="Forward QEMU's opt-in one-register frame fast path switch.",
    )
    parser.add_argument(
        "--qemu-frame-restore-host-load",
        action="store_true",
        default=_env_bool(
            "SPEC_QEMU_FRAME_RESTORE_HOST_LOAD",
            _env_bool("LINX_SPEC_QEMU_FRAME_RESTORE_HOST_LOAD", False),
        ),
        help="Forward QEMU's opt-in cached host-load frame restore experiment.",
    )
    parser.add_argument("--qemu-tlb-stats", action="store_true", default=_env_bool("SPEC_QEMU_TLB_STATS", _env_bool("LINX_SPEC_QEMU_TLB_STATS", False)))
    parser.add_argument(
        "--qemu-tlb-inv-hot",
        action="store_true",
        default=_env_bool(
            "SPEC_QEMU_TLB_INV_HOT",
            _env_bool("LINX_SPEC_QEMU_TLB_INV_HOT", False),
        ),
        help="Forward QEMU's opt-in TLBI source-PC hot-site heartbeat sketch.",
    )
    parser.add_argument(
        "--qemu-tlb-fill-stats",
        action="store_true",
        default=_env_bool(
            "SPEC_QEMU_TLB_FILL_STATS",
            _env_bool("LINX_SPEC_QEMU_TLB_FILL_STATS", False),
        ),
        help="Forward QEMU's opt-in demand page-walk heartbeat counters.",
    )
    parser.add_argument(
        "--qemu-tlb-fill-hot",
        action="store_true",
        default=_env_bool(
            "SPEC_QEMU_TLB_FILL_HOT",
            _env_bool("LINX_SPEC_QEMU_TLB_FILL_HOT", False),
        ),
        help="Forward QEMU's opt-in demand page-walk hot-page heartbeat sketch.",
    )
    parser.add_argument(
        "--qemu-mmu-cache",
        action="store_true",
        default=_env_bool(
            "SPEC_QEMU_MMU_CACHE",
            _env_bool("LINX_SPEC_QEMU_MMU_CACHE", False),
        ),
        help="Forward QEMU's opt-in page-walk result cache.",
    )
    parser.add_argument(
        "--qemu-mmu-cache-stats",
        action="store_true",
        default=_env_bool(
            "SPEC_QEMU_MMU_CACHE_STATS",
            _env_bool("LINX_SPEC_QEMU_MMU_CACHE_STATS", False),
        ),
        help="Forward QEMU's opt-in MMU-cache heartbeat counters.",
    )
    parser.add_argument(
        "--qemu-tlb-fault-trace",
        action="store_true",
        default=_env_bool(
            "SPEC_QEMU_TLB_FAULT_TRACE",
            _env_bool("LINX_SPEC_QEMU_TLB_FAULT_TRACE", False),
        ),
        help="Forward QEMU's opt-in page-walk fault trace.",
    )
    parser.add_argument(
        "--qemu-tlb-fault-trace-limit",
        type=int,
        default=_env_int(
            "SPEC_QEMU_TLB_FAULT_TRACE_LIMIT",
            _env_int("LINX_SPEC_QEMU_TLB_FAULT_TRACE_LIMIT", 0),
        ),
        help="Forward QEMU's page-walk fault trace line limit.",
    )
    parser.add_argument(
        "--qemu-tlb-fault-trace-addr",
        default=os.environ.get(
            "SPEC_QEMU_TLB_FAULT_TRACE_ADDR",
            os.environ.get("LINX_SPEC_QEMU_TLB_FAULT_TRACE_ADDR", ""),
        ),
        help="Forward exact virtual address filter for QEMU TLB fault trace.",
    )
    parser.add_argument(
        "--qemu-tlb-fault-trace-addr-lo",
        default=os.environ.get(
            "SPEC_QEMU_TLB_FAULT_TRACE_ADDR_LO",
            os.environ.get("LINX_SPEC_QEMU_TLB_FAULT_TRACE_ADDR_LO", ""),
        ),
        help="Forward low virtual address filter for QEMU TLB fault trace.",
    )
    parser.add_argument(
        "--qemu-tlb-fault-trace-addr-hi",
        default=os.environ.get(
            "SPEC_QEMU_TLB_FAULT_TRACE_ADDR_HI",
            os.environ.get("LINX_SPEC_QEMU_TLB_FAULT_TRACE_ADDR_HI", ""),
        ),
        help="Forward high virtual address filter for QEMU TLB fault trace.",
    )
    parser.add_argument(
        "--qemu-tlb-fault-trace-count-lo",
        default=os.environ.get(
            "SPEC_QEMU_TLB_FAULT_TRACE_COUNT_LO",
            os.environ.get("LINX_SPEC_QEMU_TLB_FAULT_TRACE_COUNT_LO", ""),
        ),
        help="Forward low instruction-count filter for QEMU TLB fault trace.",
    )
    parser.add_argument(
        "--qemu-tlb-fault-trace-count-hi",
        default=os.environ.get(
            "SPEC_QEMU_TLB_FAULT_TRACE_COUNT_HI",
            os.environ.get("LINX_SPEC_QEMU_TLB_FAULT_TRACE_COUNT_HI", ""),
        ),
        help="Forward high instruction-count filter for QEMU TLB fault trace.",
    )
    parser.add_argument(
        "--qemu-tb-stats",
        action="store_true",
        default=_env_bool(
            "SPEC_QEMU_TB_STATS",
            _env_bool("LINX_SPEC_QEMU_TB_STATS", False),
        ),
        help="Forward QEMU's opt-in TCG TB heartbeat counters.",
    )
    parser.add_argument("--no-progress-timeout", type=float, default=_env_float("SPEC_NO_PROGRESS_TIMEOUT", _env_float("LINX_SPEC_NO_PROGRESS_TIMEOUT", 0.0)))
    parser.add_argument(
        "--stack-limit",
        default=os.environ.get(
            "SPEC_STACK_LIMIT",
            os.environ.get("LINX_SPEC_STACK_LIMIT_BYTES", os.environ.get("LINX_SPEC_STACK_LIMIT", "")),
        ),
        help="SPEC init wrapper stack limit passed through to the matrix runner.",
    )
    parser.add_argument("--guest-heartbeat-sec", type=int, default=_env_int("SPEC_GUEST_HEARTBEAT_SEC", _env_int("LINX_SPEC_GUEST_HEARTBEAT_SEC", 60)))
    parser.add_argument("--symbolize-heartbeat", action="store_true", default=os.environ.get("LINX_SPEC_SYMBOLIZE_HEARTBEAT", "").lower() in {"1", "true", "yes", "on"})
    parser.add_argument("--dump-prefix-bytes", type=int, default=_env_int("SPEC_DUMP_PREFIX_BYTES", _env_int("LINX_SPEC_DUMP_PREFIX_BYTES", 0)))
    parser.add_argument("--transports", default="", help="Override each suite transport list, e.g. initramfs or 9p,initramfs.")
    parser.add_argument(
        "--fail-9p-timeout",
        action="store_true",
        default=_env_bool("SPEC_FAIL_9P_TIMEOUT", _env_bool("LINX_SPEC_FAIL_9P_TIMEOUT", False)),
        help=(
            "Pass --fail-9p-timeout to matrix runners. Generated large 9p "
            "shards enable this automatically unless --transports overrides the split policy."
        ),
    )
    parser.add_argument("--continue-on-fail", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.heartbeat_sec < 0:
        raise SystemExit("error: --heartbeat-sec must be >= 0")
    if args.memory_mb <= 0:
        raise SystemExit("error: --memory-mb must be > 0")
    if args.qemu_heartbeat_interval < 0:
        raise SystemExit("error: --qemu-heartbeat-interval must be >= 0")
    if args.qemu_heartbeat_code_bytes < 0:
        raise SystemExit("error: --qemu-heartbeat-code-bytes must be >= 0")
    if args.qemu_heartbeat_same_site_warn < 0:
        raise SystemExit("error: --qemu-heartbeat-same-site-warn must be >= 0")
    if args.no_progress_timeout < 0:
        raise SystemExit("error: --no-progress-timeout must be >= 0")
    if args.guest_heartbeat_sec < 0:
        raise SystemExit("error: --guest-heartbeat-sec must be >= 0")
    if args.dump_prefix_bytes < 0:
        raise SystemExit("error: --dump-prefix-bytes must be >= 0")

    spec_dir = Path(os.path.expanduser(args.spec_dir)).resolve()
    runner = Path(os.path.expanduser(args.runner)).resolve()
    qemu = Path(os.path.expanduser(args.qemu)).resolve()
    sysroot = Path(os.path.expanduser(args.sysroot)).resolve()
    out_dir = Path(os.path.expanduser(args.out_dir)).resolve()

    if not runner.is_file():
        raise SystemExit(f"error: missing SPEC matrix runner: {runner}")
    if not spec_dir.exists():
        raise SystemExit(f"error: missing SPEC dir: {spec_dir}")
    if not qemu.exists():
        raise SystemExit(f"error: missing QEMU binary: {qemu}")

    runner_has_qemu_heartbeat = _runner_supports_option(runner, "--qemu-heartbeat-interval")
    runner_has_qemu_heartbeat_regs = _runner_supports_option(runner, "--qemu-heartbeat-regs")
    runner_has_qemu_heartbeat_code_bytes = _runner_supports_option(runner, "--qemu-heartbeat-code-bytes")
    runner_has_qemu_heartbeat_same_site_warn = _runner_supports_option(runner, "--qemu-heartbeat-same-site-warn")
    runner_has_qemu_frame_stats = _runner_supports_option(runner, "--qemu-frame-stats")
    runner_has_qemu_frame_shape_hot = _runner_supports_option(runner, "--qemu-frame-shape-hot")
    runner_has_qemu_frame_single_reg_fast = _runner_supports_option(runner, "--qemu-frame-single-reg-fast")
    runner_has_qemu_frame_restore_host_load = _runner_supports_option(runner, "--qemu-frame-restore-host-load")
    runner_has_qemu_tlb_stats = _runner_supports_option(runner, "--qemu-tlb-stats")
    runner_has_qemu_tlb_inv_hot = _runner_supports_option(runner, "--qemu-tlb-inv-hot")
    runner_has_qemu_tlb_fill_stats = _runner_supports_option(runner, "--qemu-tlb-fill-stats")
    runner_has_qemu_tlb_fill_hot = _runner_supports_option(runner, "--qemu-tlb-fill-hot")
    runner_has_qemu_mmu_cache = _runner_supports_option(runner, "--qemu-mmu-cache")
    runner_has_qemu_mmu_cache_stats = _runner_supports_option(
        runner, "--qemu-mmu-cache-stats"
    )
    runner_has_qemu_tlb_fault_trace = _runner_supports_option(runner, "--qemu-tlb-fault-trace")
    runner_has_qemu_tlb_fault_trace_filters = _runner_supports_option(
        runner, "--qemu-tlb-fault-trace-addr-lo"
    )
    runner_has_qemu_tb_stats = _runner_supports_option(runner, "--qemu-tb-stats")
    runner_has_no_progress = _runner_supports_option(runner, "--no-progress-timeout")
    runner_has_memory_mb = _runner_supports_option(runner, "--memory-mb")
    runner_has_stack_limit = _runner_supports_option(runner, "--stack-limit")
    runner_has_symbolize_heartbeat = _runner_supports_option(runner, "--symbolize-heartbeat")
    runner_has_fail_9p_timeout = _runner_supports_option(runner, "--fail-9p-timeout")
    if args.qemu_heartbeat_interval and not runner_has_qemu_heartbeat:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-heartbeat-interval; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the heartbeat switch"
        )
    if args.qemu_heartbeat_regs and not runner_has_qemu_heartbeat_regs:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-heartbeat-regs; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the heartbeat register switch"
        )
    if args.qemu_heartbeat_code_bytes and not runner_has_qemu_heartbeat_code_bytes:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-heartbeat-code-bytes; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the heartbeat code-byte switch"
        )
    if args.qemu_heartbeat_same_site_warn and not runner_has_qemu_heartbeat_same_site_warn:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-heartbeat-same-site-warn; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the heartbeat stall switch"
        )
    if args.qemu_frame_stats and not runner_has_qemu_frame_stats:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-frame-stats; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the frame-stats switch"
        )
    if args.qemu_frame_shape_hot and not runner_has_qemu_frame_shape_hot:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-frame-shape-hot; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the frame-shape hot-site switch"
        )
    if args.qemu_frame_single_reg_fast and not runner_has_qemu_frame_single_reg_fast:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-frame-single-reg-fast; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the one-register frame fast-path switch"
        )
    if args.qemu_frame_restore_host_load and not runner_has_qemu_frame_restore_host_load:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-frame-restore-host-load; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the frame restore host-load switch"
        )
    if args.qemu_tlb_stats and not runner_has_qemu_tlb_stats:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-tlb-stats; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the TLB stats switch"
        )
    if args.qemu_tlb_inv_hot and not runner_has_qemu_tlb_inv_hot:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-tlb-inv-hot; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the TLB invalidation hot-site switch"
        )
    if args.qemu_tlb_fill_stats and not runner_has_qemu_tlb_fill_stats:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-tlb-fill-stats; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the TLB fill stats switch"
        )
    if args.qemu_tlb_fill_hot and not runner_has_qemu_tlb_fill_hot:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-tlb-fill-hot; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the TLB fill hot-site switch"
        )
    if args.qemu_mmu_cache and not runner_has_qemu_mmu_cache:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-mmu-cache; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the MMU cache switch"
        )
    if args.qemu_mmu_cache_stats and not runner_has_qemu_mmu_cache_stats:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-mmu-cache-stats; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the MMU cache stats switch"
        )
    qemu_tlb_fault_trace_filters = {
        "addr": args.qemu_tlb_fault_trace_addr.strip(),
        "addr_lo": args.qemu_tlb_fault_trace_addr_lo.strip(),
        "addr_hi": args.qemu_tlb_fault_trace_addr_hi.strip(),
        "count_lo": args.qemu_tlb_fault_trace_count_lo.strip(),
        "count_hi": args.qemu_tlb_fault_trace_count_hi.strip(),
    }
    qemu_tlb_fault_trace_filters = {
        key: value for key, value in qemu_tlb_fault_trace_filters.items() if value
    }
    qemu_tlb_fault_trace_requested = bool(
        args.qemu_tlb_fault_trace
        or args.qemu_tlb_fault_trace_limit > 0
        or qemu_tlb_fault_trace_filters
    )
    if qemu_tlb_fault_trace_requested and not runner_has_qemu_tlb_fault_trace:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-tlb-fault-trace; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the TLB fault trace switch"
        )
    if qemu_tlb_fault_trace_filters and not runner_has_qemu_tlb_fault_trace_filters:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-tlb-fault-trace-* filters; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the TLB fault trace filters"
        )
    if args.qemu_tlb_fault_trace_limit < 0:
        raise SystemExit("error: --qemu-tlb-fault-trace-limit must be >= 0")
    if args.qemu_tb_stats and not runner_has_qemu_tb_stats:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--qemu-tb-stats; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the TB stats switch"
        )
    if args.no_progress_timeout and not runner_has_no_progress:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--no-progress-timeout; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the no-progress switch"
        )
    if args.memory_mb != 2048 and not runner_has_memory_mb:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--memory-mb; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun with the default memory size"
        )
    if args.stack_limit.strip() and not runner_has_stack_limit:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--stack-limit; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the stack-limit switch"
        )
    if args.symbolize_heartbeat and not runner_has_symbolize_heartbeat:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--symbolize-heartbeat; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the symbolize-heartbeat switch"
        )
    if args.fail_9p_timeout and not runner_has_fail_9p_timeout:
        raise SystemExit(
            "error: local SPEC matrix runner does not support "
            "--fail-9p-timeout; update tools/spec2017/run_stage_qemu_matrix.py "
            "or rerun without the fail-9p-timeout switch"
        )

    suites = _select_suites(args.profile, args.suite)
    out_dir.mkdir(parents=True, exist_ok=True)

    started = _utc_now()
    t0 = time.monotonic()
    rows: list[dict[str, Any]] = []
    overall_ok = True

    for suite in suites:
        suite_ok = True
        for unit in _suite_execution_units(suite, args.transports):
            suite_out = out_dir / unit.name
            fail_9p_timeout = args.fail_9p_timeout or _auto_fail_9p_timeout(unit, args.transports)
            if fail_9p_timeout and not runner_has_fail_9p_timeout:
                raise SystemExit(
                    "error: local SPEC matrix runner does not support "
                    "--fail-9p-timeout required by the generated large 9p shard"
                )
            cmd = _suite_command(
                suite=unit,
                runner=runner,
                spec_dir=spec_dir,
                qemu=qemu,
                sysroot=sysroot,
                out_dir=out_dir,
                append_extra=args.append_extra,
                heartbeat_sec=args.heartbeat_sec,
                memory_mb=args.memory_mb,
                qemu_heartbeat_interval=args.qemu_heartbeat_interval,
                qemu_heartbeat_regs=args.qemu_heartbeat_regs,
                qemu_heartbeat_code_bytes=args.qemu_heartbeat_code_bytes,
                qemu_heartbeat_same_site_warn=args.qemu_heartbeat_same_site_warn,
                qemu_frame_stats=args.qemu_frame_stats,
                qemu_frame_shape_hot=args.qemu_frame_shape_hot,
                qemu_frame_single_reg_fast=args.qemu_frame_single_reg_fast,
                qemu_frame_restore_host_load=args.qemu_frame_restore_host_load,
                qemu_tlb_stats=args.qemu_tlb_stats,
                qemu_tlb_inv_hot=args.qemu_tlb_inv_hot,
                qemu_tlb_fill_stats=args.qemu_tlb_fill_stats,
                qemu_tlb_fill_hot=args.qemu_tlb_fill_hot,
                qemu_mmu_cache=args.qemu_mmu_cache,
                qemu_mmu_cache_stats=args.qemu_mmu_cache_stats,
                qemu_tlb_fault_trace=args.qemu_tlb_fault_trace,
                qemu_tlb_fault_trace_limit=args.qemu_tlb_fault_trace_limit,
                qemu_tlb_fault_trace_addr=args.qemu_tlb_fault_trace_addr,
                qemu_tlb_fault_trace_addr_lo=args.qemu_tlb_fault_trace_addr_lo,
                qemu_tlb_fault_trace_addr_hi=args.qemu_tlb_fault_trace_addr_hi,
                qemu_tlb_fault_trace_count_lo=args.qemu_tlb_fault_trace_count_lo,
                qemu_tlb_fault_trace_count_hi=args.qemu_tlb_fault_trace_count_hi,
                qemu_tb_stats=args.qemu_tb_stats,
                no_progress_timeout=args.no_progress_timeout,
                forward_memory_mb=runner_has_memory_mb,
                forward_qemu_heartbeat=runner_has_qemu_heartbeat,
                forward_qemu_heartbeat_regs=runner_has_qemu_heartbeat_regs,
                forward_qemu_heartbeat_code_bytes=runner_has_qemu_heartbeat_code_bytes,
                forward_qemu_heartbeat_same_site_warn=runner_has_qemu_heartbeat_same_site_warn,
                forward_qemu_frame_stats=runner_has_qemu_frame_stats,
                forward_qemu_frame_shape_hot=runner_has_qemu_frame_shape_hot,
                forward_qemu_frame_single_reg_fast=runner_has_qemu_frame_single_reg_fast,
                forward_qemu_frame_restore_host_load=runner_has_qemu_frame_restore_host_load,
                forward_qemu_tlb_stats=runner_has_qemu_tlb_stats,
                forward_qemu_tlb_inv_hot=runner_has_qemu_tlb_inv_hot,
                forward_qemu_tlb_fill_stats=runner_has_qemu_tlb_fill_stats,
                forward_qemu_tlb_fill_hot=runner_has_qemu_tlb_fill_hot,
                forward_qemu_mmu_cache=runner_has_qemu_mmu_cache,
                forward_qemu_mmu_cache_stats=runner_has_qemu_mmu_cache_stats,
                forward_qemu_tlb_fault_trace=runner_has_qemu_tlb_fault_trace,
                forward_qemu_tb_stats=runner_has_qemu_tb_stats,
                forward_no_progress=runner_has_no_progress,
                forward_stack_limit=runner_has_stack_limit,
                forward_symbolize_heartbeat=runner_has_symbolize_heartbeat,
                stack_limit=args.stack_limit,
                symbolize_heartbeat=args.symbolize_heartbeat,
                guest_heartbeat_sec=args.guest_heartbeat_sec,
                dump_prefix_bytes=args.dump_prefix_bytes,
                fail_9p_timeout=fail_9p_timeout,
            )
            print(f"-- {unit.name}: {unit.description}")
            print(" ".join(cmd))
            suite_start = time.monotonic()
            if args.dry_run:
                rc = 0
                matrix = {"ok": True, "loaded": False, "dry_run": True}
            else:
                proc = subprocess.run(cmd, check=False)
                rc = proc.returncode
                matrix = _read_matrix_summary(suite_out / "qemu_matrix_summary.json")
            row_ok = rc == 0 and bool(matrix.get("ok", False))
            failure_classes = _matrix_failure_classes(matrix)
            failure_details = _matrix_failure_details(matrix)
            rows.append(
                {
                    "name": unit.name,
                    "source_suite": suite.name,
                    "description": unit.description,
                    "stage": unit.stage,
                    "input_set": unit.input_set,
                    "benches": list(unit.benches),
                    "transports": unit.transports,
                    "timeout_sec": _env_int(unit.timeout_env, unit.timeout_default),
                    "command": cmd,
                    "returncode": rc,
                    "ok": row_ok,
                    "elapsed_sec": round(time.monotonic() - suite_start, 3),
                    "out_dir": str(suite_out),
                    "matrix_summary": str(suite_out / "qemu_matrix_summary.json"),
                    "matrix_loaded": bool(matrix.get("loaded", False)),
                    "matrix_ok": bool(matrix.get("ok", False)),
                    "failure_classes": failure_classes,
                    "failure_details": failure_details,
                    "fail_9p_timeout": fail_9p_timeout,
                }
            )
            suite_ok = suite_ok and row_ok
        overall_ok = overall_ok and suite_ok
        if not suite_ok and not args.continue_on_fail:
            break

    summary = {
        "schema_version": "linx-specint-fast-gate-v1",
        "profile": args.profile,
        "started_at_utc": started,
        "finished_at_utc": _utc_now(),
        "elapsed_sec": round(time.monotonic() - t0, 3),
        "dry_run": bool(args.dry_run),
        "ok": overall_ok,
        "spec_dir": str(spec_dir),
        "qemu": str(qemu),
        "qemu_provenance": qemu_binary_provenance(REPO_ROOT, qemu),
        "qemu_machine_extra": os.environ.get("LINX_SPEC_QEMU_MACHINE_EXTRA", "").strip(),
        "qemu_extra_args": _qemu_extra_args(),
        "sysroot": str(sysroot),
        "memory_mb": args.memory_mb,
        "append_extra": args.append_extra,
        "stack_limit": args.stack_limit.strip() or "default",
        "qemu_heartbeat_interval": args.qemu_heartbeat_interval,
        "qemu_heartbeat_regs": bool(args.qemu_heartbeat_regs),
        "qemu_heartbeat_code_bytes": args.qemu_heartbeat_code_bytes,
        "qemu_heartbeat_same_site_warn": args.qemu_heartbeat_same_site_warn,
        "qemu_frame_stats": bool(args.qemu_frame_stats),
        "qemu_frame_shape_hot": bool(args.qemu_frame_shape_hot),
        "qemu_frame_single_reg_fast": bool(args.qemu_frame_single_reg_fast),
        "qemu_frame_restore_host_load": bool(args.qemu_frame_restore_host_load),
        "qemu_tlb_stats": bool(args.qemu_tlb_stats),
        "qemu_tlb_inv_hot": bool(args.qemu_tlb_inv_hot),
        "qemu_tlb_fill_stats": bool(args.qemu_tlb_fill_stats),
        "qemu_tlb_fill_hot": bool(args.qemu_tlb_fill_hot),
        "qemu_mmu_cache": bool(args.qemu_mmu_cache),
        "qemu_mmu_cache_stats": bool(args.qemu_mmu_cache_stats),
        "qemu_tlb_fault_trace": bool(qemu_tlb_fault_trace_requested),
        "qemu_tlb_fault_trace_limit": args.qemu_tlb_fault_trace_limit,
        "qemu_tlb_fault_trace_filters": qemu_tlb_fault_trace_filters,
        "qemu_tb_stats": bool(args.qemu_tb_stats),
        "no_progress_timeout": args.no_progress_timeout,
        "guest_heartbeat_sec": args.guest_heartbeat_sec,
        "symbolize_heartbeat": bool(args.symbolize_heartbeat),
        "fail_9p_timeout": bool(args.fail_9p_timeout),
        "suites": rows,
    }
    summary_json = out_dir / "specint_fast_gate_summary.json"
    summary_md = out_dir / "specint_fast_gate_summary.md"
    summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_md(summary_md, summary)
    print(f"summary_json={summary_json}")
    print(f"summary_md={summary_md}")
    print(f"ok={str(overall_ok).lower()}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
