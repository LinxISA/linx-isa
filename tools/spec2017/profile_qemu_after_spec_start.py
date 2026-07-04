#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shlex
import shutil
import signal
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
    result: dict[str, Any] = {
        "ok": proc.returncode == 0 and out_file.exists(),
        "returncode": proc.returncode,
        "elapsed_sec": round(time.monotonic() - started, 3),
        "command": cmd,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }
    if result["ok"]:
        sample_text = out_file.read_text(encoding="utf-8", errors="replace")
        top_stack = _parse_top_stack_sample(sample_text)
        result["top_stack"] = top_stack
        result["top_stack_qemu"] = [
            row
            for row in top_stack
            if row.get("image", "").startswith("qemu-system-linx")
        ][:40]
        result["top_stack_unknown"] = [
            row for row in top_stack if row.get("image") == "<unknown binary>"
        ][:40]
    return result


def _terminate_wrapped_command(proc: subprocess.Popen[Any], grace_sec: float) -> dict[str, Any]:
    if proc.poll() is not None:
        return {
            "attempted": False,
            "returncode": proc.returncode,
            "reason": "already-exited",
        }

    result: dict[str, Any] = {
        "attempted": True,
        "grace_sec": grace_sec,
        "returncode": None,
        "signal": "SIGTERM",
        "killed": False,
        "target": "process-group",
    }
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except (OSError, ProcessLookupError):
        result["target"] = "process"
        proc.terminate()

    try:
        result["returncode"] = proc.wait(timeout=grace_sec)
        return result
    except subprocess.TimeoutExpired:
        result["killed"] = True
        result["signal"] = "SIGKILL"
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (OSError, ProcessLookupError):
            proc.kill()
        result["returncode"] = proc.wait()
        return result


def _wait_for_sample_delay(
    proc: subprocess.Popen[Any],
    delay_sec: float,
    poll_sec: float,
) -> dict[str, Any]:
    started = time.monotonic()
    result: dict[str, Any] = {
        "requested_sec": delay_sec,
        "elapsed_sec": 0.0,
        "completed": True,
        "command_exited": False,
        "returncode": None,
    }
    if delay_sec <= 0:
        result["command_exited"] = proc.poll() is not None
        result["returncode"] = proc.returncode
        return result

    deadline = started + delay_sec
    while True:
        proc_returncode = proc.poll()
        now = time.monotonic()
        result["elapsed_sec"] = round(now - started, 3)
        if proc_returncode is not None:
            result["completed"] = False
            result["command_exited"] = True
            result["returncode"] = proc_returncode
            return result
        remaining = deadline - now
        if remaining <= 0:
            return result
        time.sleep(min(poll_sec, remaining))


def _parse_top_stack_sample(text: str, limit: int = 120) -> list[dict[str, Any]]:
    marker = "Sort by top of stack, same collapsed"
    lines = text.splitlines()
    start: int | None = None
    for idx, line in enumerate(lines):
        if line.startswith(marker):
            start = idx + 1
            break
    if start is None:
        return []

    rows: list[dict[str, Any]] = []
    for raw in lines[start:]:
        if not raw.strip():
            if rows:
                break
            continue
        if raw.startswith("Sort by "):
            break
        parsed = _parse_top_stack_line(raw)
        if parsed is None:
            if rows:
                break
            continue
        rows.append(parsed)
        if len(rows) >= limit:
            break
    return rows


def _parse_top_stack_line(raw: str) -> dict[str, Any] | None:
    text = raw.strip()
    count_text = text.rsplit(None, 1)
    if len(count_text) != 2:
        return None
    body, count_s = count_text
    try:
        count = int(count_s)
    except ValueError:
        return None

    marker = "  (in "
    if marker not in body:
        return None
    symbol, rest = body.split(marker, 1)
    image, sep, tail = rest.partition(")")
    if not sep:
        return None
    address = None
    tail = tail.strip()
    if tail.startswith("["):
        close = tail.find("]")
        if close > 1:
            address = tail[1:close]
    return {
        "symbol": symbol.strip(),
        "image": image.strip(),
        "address": address,
        "count": count,
        "raw": raw.strip(),
    }


def _profile_exit_code(proc_returncode: int, report: dict[str, Any]) -> int:
    termination = report.get("termination") or {}
    if (
        report.get("terminate_after_sample")
        and termination.get("attempted")
        and report.get("sample", {}).get("ok")
    ):
        return 0
    if report.get("wait_timed_out") and report.get("terminate_on_wait_timeout"):
        return 2
    if proc_returncode != 0:
        return proc_returncode
    return 0 if report.get("ok") else 2


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
    ap.add_argument("--sample-delay-sec", type=float, default=0.0,
                    help="Seconds to wait after the marker is observed before sampling.")
    ap.add_argument("--terminate-after-sample", action="store_true",
                    help="Terminate the wrapped command after sample collection instead of waiting for normal completion.")
    ap.add_argument("--terminate-on-wait-timeout", action="store_true",
                    help="Terminate the wrapped command if marker/qemu are not both observed before --wait-timeout.")
    ap.add_argument("--terminate-grace-sec", type=float, default=5.0,
                    help="Grace period after SIGTERM before SIGKILL when --terminate-after-sample is used.")
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
    if args.sample_delay_sec < 0:
        raise SystemExit("error: --sample-delay-sec must be non-negative")
    if args.terminate_grace_sec < 0:
        raise SystemExit("error: --terminate-grace-sec must be non-negative")
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
        "wait_timeout_sec": args.wait_timeout,
        "wait_timed_out": False,
        "sample_delay_sec": args.sample_delay_sec,
        "sample_delay": None,
        "sample": None,
        "terminate_after_sample": bool(args.terminate_after_sample),
        "terminate_on_wait_timeout": bool(args.terminate_on_wait_timeout),
        "termination": None,
    }

    proc = subprocess.Popen(args.command, start_new_session=True)
    sample_done = False
    proc_returncode: int | None = None
    try:
        deadline = started + args.wait_timeout
        deadline_expired = False
        while time.monotonic() < deadline:
            marker_log = _find_marker_log(args.out_root, args.marker)
            qemu_pid = _find_qemu_descendant(proc.pid, args.qemu_name)
            if marker_log is not None:
                report["marker_log"] = str(marker_log)
            if qemu_pid is not None:
                report["qemu_pid"] = qemu_pid
            if marker_log is not None and qemu_pid is not None:
                if args.sample_delay_sec > 0:
                    report["sample_delay"] = _wait_for_sample_delay(
                        proc, args.sample_delay_sec, args.poll_sec
                    )
                    if not report["sample_delay"]["completed"]:
                        break
                    refreshed_qemu_pid = _find_qemu_descendant(proc.pid, args.qemu_name)
                    if refreshed_qemu_pid is not None:
                        qemu_pid = refreshed_qemu_pid
                        report["qemu_pid"] = qemu_pid
                report["sample"] = _run_sample(qemu_pid, args.sample_sec, args.sample_out)
                sample_done = True
                if args.terminate_after_sample:
                    report["termination"] = _terminate_wrapped_command(
                        proc, args.terminate_grace_sec
                    )
                    proc_returncode = int(report["termination"]["returncode"])
                break
            if proc.poll() is not None:
                break
            time.sleep(args.poll_sec)
        else:
            deadline_expired = True

        if not sample_done and deadline_expired and proc.poll() is None:
            report["wait_timed_out"] = True
            if args.terminate_on_wait_timeout:
                report["termination"] = _terminate_wrapped_command(
                    proc, args.terminate_grace_sec
                )
                proc_returncode = int(report["termination"]["returncode"])

        if proc_returncode is None:
            proc_returncode = proc.wait()
    except KeyboardInterrupt:
        report["termination"] = _terminate_wrapped_command(proc, args.terminate_grace_sec)
        raise
    finally:
        report["finished_at_utc"] = _utc_now()
        report["elapsed_sec"] = round(time.monotonic() - started, 3)

    report["command_returncode"] = proc_returncode
    if not sample_done:
        report["sample"] = {
            "ok": False,
            "returncode": None,
            "error": (
                "marker and qemu descendant were not both observed before "
                "command exit or wait timeout"
            ),
        }
    report["ok"] = bool(report.get("sample", {}).get("ok"))
    report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return _profile_exit_code(proc_returncode, report)


if __name__ == "__main__":
    raise SystemExit(main())
