#!/usr/bin/env python3
"""Profile QEMU after SPEC start markers across a SPECint train suite."""
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
BRINGUP_DIR = REPO_ROOT / "tools" / "bringup"
if str(BRINGUP_DIR) not in sys.path:
    sys.path.insert(0, str(BRINGUP_DIR))

from qemu_build_paths import default_qemu_binary, qemu_binary_provenance

PROFILE_WRAPPER = SCRIPT_DIR / "profile_qemu_after_spec_start.py"
MATRIX_RUNNER = SCRIPT_DIR / "run_stage_qemu_matrix.py"
DEFAULT_SPEC_DIR = REPO_ROOT / "workloads" / "spec2017" / "cpu2017v118_x64_gcc12_avx2"
DEFAULT_SYSROOT = REPO_ROOT / "out" / "libc" / "musl" / "install" / "phase-b"

SPECINT_STAGE_B_WORKLOAD_BENCHES = (
    "500.perlbench_r",
    "502.gcc_r",
    "505.mcf_r",
    "520.omnetpp_r",
    "523.xalancbmk_r",
    "525.x264_r",
    "531.deepsjeng_r",
    "541.leela_r",
    "557.xz_r",
)

SPECINT_STAGE_B_SENTINELS = (
    "999.specrand_ir",
)

SPECINT_STAGE_B_BENCHES = SPECINT_STAGE_B_WORKLOAD_BENCHES + SPECINT_STAGE_B_SENTINELS
DEFAULT_PROFILE_BENCHES = SPECINT_STAGE_B_WORKLOAD_BENCHES

LARGE_PAYLOAD_TRANSPORTS = {
    "525.x264_r": "9p",
}


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


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
    return str(default_qemu_binary(REPO_ROOT).resolve())


def _bench_slug(bench: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in bench).strip("_")


def _transport_for_bench(bench: str, transports: str) -> str:
    if transports and transports != "auto":
        return transports
    return LARGE_PAYLOAD_TRANSPORTS.get(bench, "initramfs")


def _parse_env_assignment(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise SystemExit(f"error: --qemu-env expects KEY=VALUE, got {value!r}")
    key, val = value.split("=", 1)
    key = key.strip()
    if not key:
        raise SystemExit(f"error: --qemu-env expects non-empty KEY, got {value!r}")
    return key, val


def _add_bool(cmd: list[str], enabled: bool, option: str) -> None:
    if enabled:
        cmd.append(option)


def _profile_command(args: argparse.Namespace, bench: str, bench_root: Path) -> list[str]:
    transport = _transport_for_bench(bench, args.transports)
    sample_out = bench_root / "profile" / f"qemu-{_bench_slug(bench)}.sample.txt"
    report_out = bench_root / "profile" / f"qemu-{_bench_slug(bench)}.sample.json"
    matrix_out = bench_root / "matrix"

    cmd = [
        sys.executable,
        str(PROFILE_WRAPPER),
        "--out-root",
        str(bench_root),
        "--sample-out",
        str(sample_out),
        "--report-out",
        str(report_out),
        "--sample-sec",
        str(args.sample_sec),
        "--sample-delay-sec",
        str(args.sample_delay_sec),
        "--wait-timeout",
        str(args.wait_timeout),
        "--terminate-grace-sec",
        str(args.terminate_grace_sec),
    ]
    if args.terminate_after_sample:
        cmd.append("--terminate-after-sample")
    if args.terminate_on_wait_timeout:
        cmd.append("--terminate-on-wait-timeout")

    cmd.extend(
        [
            "--",
            sys.executable,
            str(MATRIX_RUNNER),
            "--spec-dir",
            str(args.spec_dir),
            "--qemu",
            str(args.qemu),
            "--stage",
            args.stage,
            "--input-set",
            args.input_set,
            "--transports",
            transport,
            "--bench",
            bench,
            "--sysroot",
            str(args.sysroot),
            "--timeout",
            str(args.row_timeout),
            "--heartbeat-sec",
            str(args.heartbeat_sec),
            "--guest-heartbeat-sec",
            str(args.guest_heartbeat_sec),
            "--qemu-heartbeat-interval",
            str(args.qemu_heartbeat_interval),
            "--no-progress-timeout",
            str(args.no_progress_timeout),
            "--stack-limit",
            args.stack_limit,
            "--memory-mb",
            str(args.memory_mb),
            "--append-extra",
            args.append_extra,
            "--dump-prefix-bytes",
            str(args.dump_prefix_bytes),
            "--out-dir",
            str(matrix_out),
        ]
    )
    _add_bool(cmd, args.template_chain, "--template-chain")
    _add_bool(cmd, args.qemu_frame_stats, "--qemu-frame-stats")
    _add_bool(cmd, args.qemu_frame_shape_hot, "--qemu-frame-shape-hot")
    _add_bool(cmd, args.qemu_frame_single_reg_fast, "--qemu-frame-single-reg-fast")
    _add_bool(cmd, args.qemu_frame_page_fast, "--qemu-frame-page-fast")
    _add_bool(
        cmd,
        args.qemu_frame_single_restore_host_load,
        "--qemu-frame-single-restore-host-load",
    )
    _add_bool(cmd, args.qemu_mmu_cache, "--qemu-mmu-cache")
    _add_bool(cmd, args.qemu_mmu_cache_stats, "--qemu-mmu-cache-stats")
    _add_bool(cmd, args.qemu_mmu_cache_assoc2, "--qemu-mmu-cache-assoc2")
    _add_bool(cmd, args.qemu_mmu_cache_victim, "--qemu-mmu-cache-victim")
    _add_bool(cmd, args.qemu_tb_stats, "--qemu-tb-stats")
    _add_bool(cmd, args.qemu_tlb_stats, "--qemu-tlb-stats")
    _add_bool(cmd, args.qemu_tlb_inv_hot, "--qemu-tlb-inv-hot")
    _add_bool(cmd, args.qemu_tlb_fill_stats, "--qemu-tlb-fill-stats")
    _add_bool(cmd, args.qemu_tlb_fill_hot, "--qemu-tlb-fill-hot")
    return cmd


def _top_qemu_symbols(report: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    sample = report.get("sample") or {}
    rows = sample.get("top_stack_qemu") or []
    return [
        {
            "symbol": row.get("symbol"),
            "count": row.get("count"),
        }
        for row in rows[:limit]
    ]


def _report_path_for(bench_root: Path, bench: str) -> Path:
    return bench_root / "profile" / f"qemu-{_bench_slug(bench)}.sample.json"


def _summarize_bench(bench: str, transport: str, report_path: Path,
                     returncode: int, elapsed_sec: float) -> dict[str, Any]:
    report: dict[str, Any] = {}
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    sample = report.get("sample") or {}
    termination = report.get("termination") or {}
    return {
        "bench": bench,
        "transport": transport,
        "returncode": returncode,
        "elapsed_sec": round(elapsed_sec, 3),
        "ok": bool(report.get("ok")) and returncode == 0,
        "report": str(report_path),
        "marker_log": report.get("marker_log"),
        "qemu_pid": report.get("qemu_pid"),
        "sample_ok": bool(sample.get("ok")),
        "sample_elapsed_sec": sample.get("elapsed_sec"),
        "sample_delay": report.get("sample_delay"),
        "wait_timed_out": bool(report.get("wait_timed_out")),
        "command_returncode": report.get("command_returncode"),
        "termination": termination,
        "top_qemu": _top_qemu_symbols(report, 12),
    }


def _aggregate_top(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    totals: dict[str, dict[str, int]] = {}
    for row in rows:
        seen: set[str] = set()
        for top in row.get("top_qemu") or []:
            symbol = top.get("symbol")
            count = top.get("count")
            if not symbol or not isinstance(count, int):
                continue
            slot = totals.setdefault(symbol, {"count": 0, "reports": 0})
            slot["count"] += count
            if symbol not in seen:
                slot["reports"] += 1
                seen.add(symbol)
    return [
        {"symbol": symbol, "count": values["count"], "reports": values["reports"]}
        for symbol, values in sorted(
            totals.items(),
            key=lambda item: (-item[1]["count"], item[0]),
        )
    ]


def _qemu_features(args: argparse.Namespace) -> dict[str, bool]:
    return {
        "template_chain": bool(args.template_chain),
        "qemu_frame_stats": bool(args.qemu_frame_stats),
        "qemu_frame_shape_hot": bool(args.qemu_frame_shape_hot),
        "qemu_frame_single_reg_fast": bool(args.qemu_frame_single_reg_fast),
        "qemu_frame_page_fast": bool(args.qemu_frame_page_fast),
        "qemu_frame_single_restore_host_load": bool(args.qemu_frame_single_restore_host_load),
        "qemu_mmu_cache": bool(args.qemu_mmu_cache),
        "qemu_mmu_cache_stats": bool(args.qemu_mmu_cache_stats),
        "qemu_mmu_cache_assoc2": bool(args.qemu_mmu_cache_assoc2),
        "qemu_mmu_cache_victim": bool(args.qemu_mmu_cache_victim),
        "qemu_tb_stats": bool(args.qemu_tb_stats),
        "qemu_tlb_stats": bool(args.qemu_tlb_stats),
        "qemu_tlb_inv_hot": bool(args.qemu_tlb_inv_hot),
        "qemu_tlb_fill_stats": bool(args.qemu_tlb_fill_stats),
        "qemu_tlb_fill_hot": bool(args.qemu_tlb_fill_hot),
    }


def _write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# SPECint QEMU Profile Suite",
        "",
        f"- started_at_utc: `{summary['started_at_utc']}`",
        f"- finished_at_utc: `{summary['finished_at_utc']}`",
        f"- input_set: `{summary['input_set']}`",
        f"- qemu: `{summary['qemu']}`",
        f"- qemu_head: `{summary.get('qemu_provenance', {}).get('qemu_repo_head')}`",
        "",
        "| Bench | Transport | OK | Sample | Delay | Top QEMU frames | Report |",
        "| --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for row in summary["rows"]:
        top = ", ".join(
            f"{item['symbol']}={item['count']}"
            for item in (row.get("top_qemu") or [])[:6]
        )
        delay = row.get("sample_delay") or {}
        delay_text = (
            f"{delay.get('elapsed_sec')}s"
            if delay.get("completed")
            else str(delay or "")
        )
        lines.append(
            "| "
            f"`{row['bench']}` | "
            f"`{row['transport']}` | "
            f"`{str(row['ok']).lower()}` | "
            f"`{str(row['sample_ok']).lower()}` | "
            f"`{delay_text}` | "
            f"`{top}` | "
            f"`{row['report']}` |"
        )

    lines.extend(["", "## Aggregate Top Frames", ""])
    for item in summary["aggregate_top_qemu"][:20]:
        lines.append(
            f"- `{item['symbol']}`: {item['count']} samples across "
            f"{item['reports']} report(s)"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-dir", type=Path, default=DEFAULT_SPEC_DIR)
    parser.add_argument("--qemu", type=Path, default=Path(_default_qemu()))
    parser.add_argument("--sysroot", type=Path, default=DEFAULT_SYSROOT)
    parser.add_argument("--out-root", type=Path, default=REPO_ROOT / "workloads" / "generated" / "specint-qemu-profile-suite")
    parser.add_argument(
        "--bench",
        action="append",
        default=[],
        help=(
            "Benchmark to profile; repeatable. Defaults to stage-b SPECint "
            "workload rows, excluding the fast correctness sentinel "
            "999.specrand_ir. Pass --bench 999.specrand_ir to profile it."
        ),
    )
    parser.add_argument("--input-set", choices=("test", "train"), default="train")
    parser.add_argument("--stage", choices=("a", "b"), default="b")
    parser.add_argument("--transports", default="auto", help="Transport override for all benches, or auto for per-bench policy.")
    parser.add_argument("--row-timeout", type=int, default=180)
    parser.add_argument("--wait-timeout", type=float, default=180.0)
    parser.add_argument("--sample-sec", type=int, default=5)
    parser.add_argument("--sample-delay-sec", type=float, default=5.0)
    parser.add_argument("--terminate-after-sample", action="store_true", default=True)
    parser.add_argument("--no-terminate-after-sample", dest="terminate_after_sample", action="store_false")
    parser.add_argument("--terminate-on-wait-timeout", action="store_true", default=True)
    parser.add_argument("--no-terminate-on-wait-timeout", dest="terminate_on_wait_timeout", action="store_false")
    parser.add_argument("--terminate-grace-sec", type=float, default=3.0)
    parser.add_argument("--heartbeat-sec", type=float, default=0.0)
    parser.add_argument("--guest-heartbeat-sec", type=int, default=0)
    parser.add_argument("--qemu-heartbeat-interval", type=int, default=0)
    parser.add_argument("--no-progress-timeout", type=float, default=0.0)
    parser.add_argument("--memory-mb", type=int, default=2048)
    parser.add_argument("--stack-limit", default="2G")
    parser.add_argument("--append-extra", default="norandmaps")
    parser.add_argument("--dump-prefix-bytes", type=int, default=0)
    parser.add_argument("--template-chain", action="store_true", default=_env_bool("LINX_SPEC_QEMU_TEMPLATE_CHAIN", False))
    parser.add_argument("--qemu-env", action="append", default=[], help="Extra QEMU environment assignment, KEY=VALUE; repeatable.")
    parser.add_argument("--qemu-frame-stats", action="store_true")
    parser.add_argument("--qemu-frame-shape-hot", action="store_true")
    parser.add_argument("--qemu-frame-single-reg-fast", action="store_true")
    parser.add_argument("--qemu-frame-page-fast", action="store_true")
    parser.add_argument("--qemu-frame-single-restore-host-load", action="store_true")
    parser.add_argument("--qemu-mmu-cache", action="store_true", default=_env_bool("LINX_SPEC_QEMU_MMU_CACHE", False))
    parser.add_argument("--qemu-mmu-cache-stats", action="store_true", default=_env_bool("LINX_SPEC_QEMU_MMU_CACHE_STATS", False))
    parser.add_argument("--qemu-mmu-cache-assoc2", action="store_true", default=_env_bool("LINX_SPEC_QEMU_MMU_CACHE_ASSOC2", False))
    parser.add_argument("--qemu-mmu-cache-victim", action="store_true", default=_env_bool("LINX_SPEC_QEMU_MMU_CACHE_VICTIM", False))
    parser.add_argument("--qemu-tb-stats", action="store_true")
    parser.add_argument("--qemu-tlb-stats", action="store_true")
    parser.add_argument("--qemu-tlb-inv-hot", action="store_true")
    parser.add_argument("--qemu-tlb-fill-stats", action="store_true")
    parser.add_argument("--qemu-tlb-fill-hot", action="store_true")
    parser.add_argument("--continue-on-fail", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.row_timeout <= 0:
        raise SystemExit("error: --row-timeout must be positive")
    if args.wait_timeout <= 0:
        raise SystemExit("error: --wait-timeout must be positive")
    if args.sample_sec <= 0:
        raise SystemExit("error: --sample-sec must be positive")
    if args.sample_delay_sec < 0:
        raise SystemExit("error: --sample-delay-sec must be non-negative")
    if args.terminate_grace_sec < 0:
        raise SystemExit("error: --terminate-grace-sec must be non-negative")
    if args.memory_mb <= 0:
        raise SystemExit("error: --memory-mb must be positive")
    if args.qemu_heartbeat_interval < 0:
        raise SystemExit("error: --qemu-heartbeat-interval must be non-negative")
    if args.no_progress_timeout < 0:
        raise SystemExit("error: --no-progress-timeout must be non-negative")

    args.spec_dir = Path(os.path.expanduser(str(args.spec_dir))).resolve()
    args.qemu = Path(os.path.expanduser(str(args.qemu))).resolve()
    args.sysroot = Path(os.path.expanduser(str(args.sysroot))).resolve()
    args.out_root = Path(os.path.expanduser(str(args.out_root))).resolve()
    args.bench = tuple(args.bench or DEFAULT_PROFILE_BENCHES)
    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    if not PROFILE_WRAPPER.is_file():
        raise SystemExit(f"error: missing profiler wrapper: {PROFILE_WRAPPER}")
    if not MATRIX_RUNNER.is_file():
        raise SystemExit(f"error: missing matrix runner: {MATRIX_RUNNER}")
    if not args.spec_dir.exists():
        raise SystemExit(f"error: missing SPEC dir: {args.spec_dir}")
    if not args.qemu.exists():
        raise SystemExit(f"error: missing QEMU binary: {args.qemu}")
    if not args.sysroot.exists():
        raise SystemExit(f"error: missing sysroot: {args.sysroot}")

    env = os.environ.copy()
    if args.template_chain:
        env["LINX_QEMU_TEMPLATE_CHAIN"] = "1"
    for item in args.qemu_env:
        key, value = _parse_env_assignment(item)
        env[key] = value

    args.out_root.mkdir(parents=True, exist_ok=True)
    started_at = _utc_now()
    rows: list[dict[str, Any]] = []
    commands: list[dict[str, Any]] = []
    overall_ok = True

    for bench in args.bench:
        bench_root = args.out_root / _bench_slug(bench)
        transport = _transport_for_bench(bench, args.transports)
        cmd = _profile_command(args, bench, bench_root)
        commands.append({"bench": bench, "transport": transport, "command": cmd})
        if args.dry_run:
            continue
        start = time.monotonic()
        proc = subprocess.run(cmd, env=env)
        elapsed = time.monotonic() - start
        report_path = _report_path_for(bench_root, bench)
        row = _summarize_bench(bench, transport, report_path, proc.returncode, elapsed)
        rows.append(row)
        if not row["ok"]:
            overall_ok = False
            if not args.continue_on_fail:
                break

    summary: dict[str, Any] = {
        "schema_version": "linx-spec-qemu-profile-suite-v1",
        "started_at_utc": started_at,
        "finished_at_utc": _utc_now(),
        "input_set": args.input_set,
        "stage": args.stage,
        "out_root": str(args.out_root),
        "spec_dir": str(args.spec_dir),
        "qemu": str(args.qemu),
        "qemu_provenance": qemu_binary_provenance(REPO_ROOT, args.qemu),
        "sysroot": str(args.sysroot),
        "sample_sec": args.sample_sec,
        "sample_delay_sec": args.sample_delay_sec,
        "terminate_after_sample": bool(args.terminate_after_sample),
        "terminate_on_wait_timeout": bool(args.terminate_on_wait_timeout),
        "template_chain": bool(args.template_chain),
        "qemu_features": _qemu_features(args),
        "dry_run": bool(args.dry_run),
        "ok": bool(overall_ok),
        "commands": commands,
        "rows": rows,
        "aggregate_top_qemu": _aggregate_top(rows),
    }
    summary_path = args.out_root / "profile_suite_summary.json"
    md_path = args.out_root / "profile_suite_summary.md"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(md_path, summary)

    if args.dry_run:
        for item in commands:
            print(shlex.join(item["command"]))
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
