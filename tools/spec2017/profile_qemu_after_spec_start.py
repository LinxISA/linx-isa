#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import shlex
import shutil
import subprocess
import sys
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _read_tail(path: Path, limit: int = 1_000_000) -> str:
    size = path.stat().st_size
    with path.open("rb") as f:
        if size > limit:
            f.seek(size - limit)
        data = f.read()
    return data.decode("utf-8", errors="replace")


def _find_marker_log(root: Path, marker: str) -> Path | None:
    if not root.exists():
        return None
    newest: tuple[float, Path] | None = None
    for path in root.rglob("qemu.log"):
        if not path.is_file():
            continue
        try:
            if marker not in _read_tail(path):
                continue
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if newest is None or mtime > newest[0]:
            newest = (mtime, path)
    return newest[1] if newest else None


def _parse_ps_table(text: str) -> dict[int, tuple[int, str]]:
    rows: dict[int, tuple[int, str]] = {}
    for raw in text.splitlines():
        parts = raw.strip().split(None, 2)
        if len(parts) < 3:
            continue
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
        except ValueError:
            continue
        rows[pid] = (ppid, parts[2])
    return rows


def _descendants(rows: dict[int, tuple[int, str]], root_pid: int) -> set[int]:
    children: dict[int, list[int]] = defaultdict(list)
    for pid, (ppid, _cmd) in rows.items():
        children[ppid].append(pid)

    out: set[int] = set()
    todo: deque[int] = deque(children.get(root_pid, []))
    while todo:
        pid = todo.popleft()
        if pid in out:
            continue
        out.add(pid)
        todo.extend(children.get(pid, []))
    return out


def _command_basename(command: str) -> str:
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split(None, 1)
    if not parts:
        return ""
    return Path(parts[0]).name


def _find_qemu_descendant(root_pid: int, qemu_names: list[str]) -> int | None:
    try:
        ps_out = subprocess.check_output(
            ["ps", "-axo", "pid=,ppid=,command="],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    rows = _parse_ps_table(ps_out)
    candidates = _descendants(rows, root_pid)
    matches: list[int] = []
    for pid in candidates:
        cmd = rows.get(pid, (0, ""))[1]
        exe = _command_basename(cmd)
        if any(exe == name for name in qemu_names):
            matches.append(pid)
    return min(matches) if matches else None


def _run_sample(pid: int, seconds: int, out_file: Path) -> dict[str, Any]:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    sample_bin = shutil.which("sample")
    if not sample_bin:
        return {
            "ok": False,
            "returncode": None,
            "error": "macOS sample tool not found on PATH",
            "command": [],
        }

    cmd = [sample_bin, str(pid), str(seconds), "1", "-file", str(out_file)]
    started = time.monotonic()
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return {
        "ok": proc.returncode == 0 and out_file.exists(),
        "returncode": proc.returncode,
        "elapsed_sec": round(time.monotonic() - started, 3),
        "command": cmd,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Profile the real qemu-system-linx64 child after LINX_SPEC_START."
    )
    ap.add_argument("--out-root", required=True, type=Path,
                    help="Run output root to scan for qemu.log files.")
    ap.add_argument("--sample-out", required=True, type=Path,
                    help="Destination for the macOS sample output.")
    ap.add_argument("--report-out", type=Path,
                    help="JSON report path. Defaults to <sample-out>.json.")
    ap.add_argument("--marker", default="LINX_SPEC_START",
                    help="QEMU-log marker that means benchmark execution started.")
    ap.add_argument("--wait-timeout", type=float, default=300.0,
                    help="Seconds to wait for marker and qemu child.")
    ap.add_argument("--poll-sec", type=float, default=0.5,
                    help="Polling interval while waiting for marker/qemu.")
    ap.add_argument("--sample-sec", type=int, default=30,
                    help="Seconds to pass to macOS sample.")
    ap.add_argument("--qemu-name", action="append",
                    default=["qemu-system-linx64", "qemu-system-linx"],
                    help="Substring used to identify the QEMU child; repeatable.")
    ap.add_argument("command", nargs=argparse.REMAINDER,
                    help="Command to launch after --.")
    args = ap.parse_args(argv)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        raise SystemExit("error: command required after --")
    if args.sample_sec <= 0:
        raise SystemExit("error: --sample-sec must be positive")
    if args.wait_timeout <= 0:
        raise SystemExit("error: --wait-timeout must be positive")
    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    report_out = args.report_out or args.sample_out.with_suffix(args.sample_out.suffix + ".json")
    report_out.parent.mkdir(parents=True, exist_ok=True)

    started = time.monotonic()
    report: dict[str, Any] = {
        "schema_version": "linx-spec-qemu-profile-v1",
        "started_at_utc": _utc_now(),
        "command": args.command,
        "out_root": str(args.out_root),
        "marker": args.marker,
        "sample_out": str(args.sample_out),
        "report_out": str(report_out),
        "qemu_pid": None,
        "marker_log": None,
        "sample": None,
    }

    proc = subprocess.Popen(args.command)
    sample_done = False
    try:
        deadline = started + args.wait_timeout
        while time.monotonic() < deadline:
            marker_log = _find_marker_log(args.out_root, args.marker)
            qemu_pid = _find_qemu_descendant(proc.pid, args.qemu_name)
            if marker_log is not None:
                report["marker_log"] = str(marker_log)
            if qemu_pid is not None:
                report["qemu_pid"] = qemu_pid
            if marker_log is not None and qemu_pid is not None:
                report["sample"] = _run_sample(qemu_pid, args.sample_sec, args.sample_out)
                sample_done = True
                break
            if proc.poll() is not None:
                break
            time.sleep(args.poll_sec)

        proc_returncode = proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        raise
    finally:
        report["finished_at_utc"] = _utc_now()
        report["elapsed_sec"] = round(time.monotonic() - started, 3)

    report["command_returncode"] = proc_returncode
    if not sample_done:
        report["sample"] = {
            "ok": False,
            "returncode": None,
            "error": "marker and qemu descendant were not both observed before command exit/timeout",
        }
    report["ok"] = bool(report.get("sample", {}).get("ok"))
    report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return proc_returncode if proc_returncode != 0 else (0 if report["ok"] else 2)


if __name__ == "__main__":
    raise SystemExit(main())
