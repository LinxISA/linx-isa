#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

import run_tsvc as core


class BatchFailure(Exception):
    def __init__(self, payload: dict[str, object]):
        super().__init__(str(payload.get("error", "TSVC batch failed")))
        self.payload = payload


def _require_matching_provenance(
    expected: dict[str, object], actual: dict[str, object], batch_index: int
) -> None:
    if expected != actual:
        raise BatchFailure(
            {
                "batch_index": batch_index,
                "status": "fail",
                "returncode": 1,
                "error": f"batch {batch_index} provenance mismatch",
                "expected_provenance": expected,
                "actual_provenance": actual,
            }
        )


def _exact_kernel_regex(kernels: list[str]) -> str:
    return "^(" + "|".join(re.escape(k) for k in kernels) + ")$"


def _resolve_kernel_list(tsvc_src_arg: str | None,
                         kernel_regex: str | None) -> tuple[Path, list[str]]:
    src_dir = core._resolve_tsvc_src(tsvc_src_arg)
    tsvc_c = src_dir / "tsvc.c"
    kernels = core._extract_kernel_names(tsvc_c.read_text(encoding="utf-8"))
    if kernel_regex:
        pat = re.compile(kernel_regex)
        kernels = [k for k in kernels if pat.search(k)]
        if not kernels:
            raise SystemExit(f"error: --kernel-regex matched 0 kernels: {kernel_regex}")
    return src_dir, kernels


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_rows(stdout_path: Path) -> dict[str, str]:
    rows = core._parse_kernel_checksums(
        stdout_path.read_text(encoding="utf-8", errors="replace"),
        expected_kernels=[],
    )
    return rows


def _passthrough_value(args: list[str], option: str) -> str | None:
    prefix = option + "="
    for idx, arg in enumerate(args):
        if arg == option and idx + 1 < len(args):
            return args[idx + 1]
        if arg.startswith(prefix):
            return arg[len(prefix):]
    return None


def _tail(path: Path, *, max_lines: int = 20) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()[-max_lines:]


def _batch_paths(batch_out: Path, mode: str) -> dict[str, Path]:
    reports_dir = batch_out / "reports" / "tsvc"
    qemu_dir = batch_out / "qemu" / "tsvc"
    logs_dir = batch_out / "logs"
    return {
        "coverage": reports_dir / "vectorization_coverage.json",
        "gate": reports_dir / "gate_result.json",
        "stdout": qemu_dir / f"tsvc.{mode}.stdout.txt",
        "stderr": qemu_dir / f"tsvc.{mode}.stderr.txt",
        "driver_stdout": logs_dir / "run_tsvc.stdout.txt",
        "driver_stderr": logs_dir / "run_tsvc.stderr.txt",
    }


def _batch_failure_payload(
    *,
    batch_index: int,
    batch_out: Path,
    kernels: list[str],
    mode: str,
    command: list[str],
    returncode: int,
    elapsed_s: float,
) -> dict[str, object]:
    paths = _batch_paths(batch_out, mode)
    observed = _parse_rows(paths["stdout"]) if paths["stdout"].exists() else {}
    return {
        "batch_index": batch_index,
        "status": "fail",
        "returncode": returncode,
        "elapsed_seconds": round(elapsed_s, 3),
        "kernel_count": len(kernels),
        "kernels": kernels,
        "observed_kernel_count": len(observed),
        "observed_kernels": sorted(observed),
        "missing_kernels": [k for k in kernels if k not in observed],
        "out_dir": str(batch_out),
        "command": " ".join(shlex.quote(c) for c in command),
        "qemu_stdout": str(paths["stdout"]) if paths["stdout"].exists() else None,
        "qemu_stderr": str(paths["stderr"]) if paths["stderr"].exists() else None,
        "driver_stdout": str(paths["driver_stdout"]),
        "driver_stderr": str(paths["driver_stderr"]),
        "driver_stderr_tail": _tail(paths["driver_stderr"]),
    }


def _run_batch(python: str,
               base_args: list[str],
               mode: str,
               src_dir: Path,
               batch_out: Path,
               kernels: list[str],
               verbose: bool,
               batch_index: int) -> dict[str, object]:
    cmd = [
        python,
        str(core.TSVC_DIR / "run_tsvc.py"),
        *base_args,
        "--vector-mode",
        mode,
        "--tsvc-src",
        str(src_dir),
        "--kernel-regex",
        _exact_kernel_regex(kernels),
        "--out-dir",
        str(batch_out),
    ]
    if verbose:
        print("+", " ".join(shlex.quote(c) for c in cmd), file=sys.stderr)
    paths = _batch_paths(batch_out, mode)
    paths["driver_stdout"].parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    p = subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed_s = time.monotonic() - start
    paths["driver_stdout"].write_text(p.stdout or "", encoding="utf-8")
    paths["driver_stderr"].write_text(p.stderr or "", encoding="utf-8")
    if p.stdout:
        sys.stdout.write(p.stdout)
        sys.stdout.flush()
    if p.stderr:
        sys.stderr.write(p.stderr)
        sys.stderr.flush()
    if p.returncode != 0:
        raise BatchFailure(
            _batch_failure_payload(
                batch_index=batch_index,
                batch_out=batch_out,
                kernels=kernels,
                mode=mode,
                command=cmd,
                returncode=p.returncode,
                elapsed_s=elapsed_s,
            )
        )

    reports_dir = batch_out / "reports" / "tsvc"
    qemu_dir = batch_out / "qemu" / "tsvc"
    coverage = _read_json(reports_dir / "vectorization_coverage.json")
    gate = _read_json(reports_dir / "gate_result.json")
    provenance = gate.get("provenance")
    if not isinstance(provenance, dict):
        raise BatchFailure(
            {
                "batch_index": batch_index,
                "status": "fail",
                "returncode": 1,
                "error": f"batch {batch_index} missing provenance receipt",
            }
        )
    try:
        core._validate_provenance_receipt(provenance, require_qemu=True)
    except SystemExit as exc:
        raise BatchFailure(
            {
                "batch_index": batch_index,
                "status": "fail",
                "returncode": 1,
                "error": f"batch {batch_index} invalid provenance: {exc}",
                "provenance": provenance,
            }
        ) from exc
    stdout_path = qemu_dir / f"tsvc.{mode}.stdout.txt"
    stderr_path = qemu_dir / f"tsvc.{mode}.stderr.txt"
    return {
        "batch_index": batch_index,
        "status": "pass",
        "returncode": p.returncode,
        "elapsed_seconds": round(elapsed_s, 3),
        "kernels": kernels,
        "coverage": coverage,
        "gate": gate,
        "provenance": provenance,
        "stdout_path": stdout_path,
        "stderr_path": stderr_path,
        "driver_stdout": paths["driver_stdout"],
        "driver_stderr": paths["driver_stderr"],
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Run TSVC in deterministic kernel batches and aggregate results."
    )
    ap.add_argument("--batch-size", type=int, default=20,
                    help="Number of kernels per batch.")
    ap.add_argument("--kernel-regex", default=None,
                    help="Optional regex to pre-filter kernels before batching.")
    ap.add_argument("--out-dir", required=True,
                    help="Aggregate output root.")
    ap.add_argument("--strict-fail-under", type=int, default=None,
                    help="Aggregate vectorized-kernel floor.")
    ap.add_argument("--tsvc-src", default=None,
                    help="TSVC source directory.")
    ap.add_argument("--vector-mode", choices=("off", "mseq", "mpar", "auto"),
                    default="auto")
    ap.add_argument("--verbose", "-v", action="store_true")
    args, passthrough = ap.parse_known_args(argv)

    if args.batch_size <= 0:
        raise SystemExit("error: --batch-size must be > 0")

    out_root = Path(os.path.expanduser(args.out_dir)).resolve()
    batch_root = out_root / "batches"
    reports_dir = out_root / "reports" / "tsvc"
    qemu_dir = out_root / "qemu" / "tsvc"
    for d in (batch_root, reports_dir, qemu_dir):
        d.mkdir(parents=True, exist_ok=True)

    src_dir, kernels = _resolve_kernel_list(args.tsvc_src, args.kernel_regex)
    batches = [
        kernels[i:i + args.batch_size]
        for i in range(0, len(kernels), args.batch_size)
    ]
    python = sys.executable or "python3"

    merged_rows: list[str] = ["Loop \tTime(sec) \tChecksum"]
    merged_stderr: list[str] = []
    vectorized = 0
    total = 0
    batch_payloads: list[dict[str, object]] = []
    expected_provenance: dict[str, object] | None = None
    provenance_error: str | None = None

    failed_batch: dict[str, object] | None = None
    started_at = time.monotonic()

    for idx, batch in enumerate(batches, start=1):
        batch_out = batch_root / f"batch_{idx:03d}"
        try:
            payload = _run_batch(
                python=python,
                base_args=passthrough,
                mode=args.vector_mode,
                src_dir=src_dir,
                batch_out=batch_out,
                kernels=batch,
                verbose=args.verbose,
                batch_index=idx,
            )
        except BatchFailure as exc:
            failed_batch = exc.payload
            batch_payloads.append(failed_batch)
            break
        batch_provenance = payload["provenance"]
        assert isinstance(batch_provenance, dict)
        if expected_provenance is None:
            expected_provenance = batch_provenance
        else:
            try:
                _require_matching_provenance(
                    expected_provenance, batch_provenance, idx
                )
            except BatchFailure as exc:
                provenance_error = str(exc)
                failed_batch = {
                    **exc.payload,
                    "elapsed_seconds": float(payload.get("elapsed_seconds", 0.0)),
                    "kernel_count": len(batch),
                    "kernels": batch,
                    "out_dir": str(batch_out),
                }
                batch_payloads.append(failed_batch)
                break
        coverage = payload["coverage"]
        vectorized += int(coverage.get("vectorized", 0))
        total += int(coverage.get("total", 0))
        stdout_path = payload["stdout_path"]
        stderr_path = payload["stderr_path"]
        stdout_text = stdout_path.read_text(encoding="utf-8", errors="replace")
        stdout_lines = stdout_text.splitlines()
        for line in stdout_lines:
            if line.startswith("Loop") or line.startswith("Time"):
                continue
            if line.strip():
                merged_rows.append(line)
        stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace")
        if stderr_text.strip():
            merged_stderr.append(f"# batch {idx:03d}")
            merged_stderr.append(stderr_text.rstrip())
        batch_payloads.append(
            {
                "batch_index": idx,
                "status": "pass",
                "returncode": int(payload.get("returncode", 0)),
                "elapsed_seconds": float(payload.get("elapsed_seconds", 0.0)),
                "kernel_count": len(batch),
                "kernels": batch,
                "out_dir": str(batch_out),
                "qemu_stdout": str(stdout_path),
                "qemu_stderr": str(stderr_path),
                "driver_stdout": str(payload["driver_stdout"]),
                "driver_stderr": str(payload["driver_stderr"]),
                "vectorized": int(coverage.get("vectorized", 0)),
                "total": int(coverage.get("total", 0)),
                "provenance": batch_provenance,
            }
        )

    merged_stdout_path = qemu_dir / f"tsvc.{args.vector_mode}.stdout.txt"
    merged_stderr_path = qemu_dir / f"tsvc.{args.vector_mode}.stderr.txt"
    merged_stdout_path.write_text("\n".join(merged_rows) + "\n", encoding="utf-8")
    merged_stderr_path.write_text(
        ("\n\n".join(merged_stderr) + "\n") if merged_stderr else "",
        encoding="utf-8",
    )

    elapsed_total_s = round(time.monotonic() - started_at, 3)
    strict_floor_failed = (
        failed_batch is None
        and args.strict_fail_under is not None
        and vectorized < args.strict_fail_under
    )
    status = "pass"
    returncode = 0
    error = None
    if failed_batch is not None:
        status = "fail"
        returncode = int(failed_batch.get("returncode", 1))
        error = str(
            failed_batch.get("error")
            or (
                f"batch {failed_batch.get('batch_index')} failed "
                f"(returncode={returncode})"
            )
        )
    elif strict_floor_failed:
        status = "fail"
        returncode = 1
        error = (
            f"aggregate vectorized kernels {vectorized} below floor "
            f"{args.strict_fail_under}"
        )

    aggregate = {
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "tool": "workloads/tsvc/run_tsvc_batched.py",
        "command": " ".join(
            [shlex.quote(python), "workloads/tsvc/run_tsvc_batched.py",
             *[shlex.quote(a) for a in argv]]
        ),
        "ok": status == "pass",
        "status": status,
        "returncode": returncode,
        "error": error,
        "elapsed_seconds": elapsed_total_s,
        "vector_mode": args.vector_mode,
        "batch_size": args.batch_size,
        "kernel_count": len(kernels),
        "vectorized": vectorized,
        "total": total,
        "strict_fail_under": args.strict_fail_under,
        "qemu_timeout_seconds": _passthrough_value(passthrough, "--qemu-timeout"),
        "completed_batches": sum(1 for b in batch_payloads if b.get("status") == "pass"),
        "failed_batch": failed_batch,
        "source": str(src_dir),
        "batches": batch_payloads,
        "provenance": expected_provenance,
        "provenance_consistent": (
            expected_provenance is not None
            and provenance_error is None
            and failed_batch is None
        ),
        "sha_manifest": (
            expected_provenance.get("sha_manifest")
            if expected_provenance is not None
            else core._build_sha_manifest()
        ),
        "merged_qemu_stdout": str(merged_stdout_path),
        "merged_qemu_stderr": str(merged_stderr_path),
    }

    gate_json = reports_dir / "gate_result.json"
    coverage_json = reports_dir / "vectorization_coverage.json"
    coverage_md = reports_dir / "vectorization_coverage.md"
    kernel_list_path = reports_dir / "kernel_list.txt"
    gate_json.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    coverage_json.write_text(
        json.dumps({"vectorized": vectorized, "total": total}, indent=2) + "\n",
        encoding="utf-8",
    )
    coverage_md.write_text(
        f"# TSVC batched coverage\n\n- Vectorized: `{vectorized}`\n- Total: `{total}`\n",
        encoding="utf-8",
    )
    kernel_list_path.write_text("\n".join(kernels) + "\n", encoding="utf-8")

    report_lines = [
        "# TSVC batched report",
        "",
        f"- Source: `{src_dir}`",
        f"- Status: `{status}`",
        f"- Return code: `{returncode}`",
        f"- Elapsed seconds: `{elapsed_total_s}`",
        f"- Vector mode: `{args.vector_mode}`",
        f"- Batch size: `{args.batch_size}`",
        f"- Kernel count: `{len(kernels)}`",
        f"- Vectorized: `{vectorized}/{total}`",
        f"- Completed batches: `{aggregate['completed_batches']}/{len(batches)}`",
        f"- Merged QEMU stdout: `{merged_stdout_path}`",
        f"- Merged QEMU stderr: `{merged_stderr_path}`",
        f"- Aggregate gate JSON: `{gate_json}`",
    ]
    if failed_batch is not None:
        report_lines.extend(
            [
                "",
                "## Failed Batch",
                f"- Batch: `{failed_batch.get('batch_index')}`",
                f"- Kernels: `{', '.join(str(k) for k in failed_batch.get('kernels', []))}`",
                f"- Observed kernels: `{failed_batch.get('observed_kernel_count')}`",
                f"- QEMU stdout: `{failed_batch.get('qemu_stdout')}`",
                f"- QEMU stderr: `{failed_batch.get('qemu_stderr')}`",
                f"- Driver stderr: `{failed_batch.get('driver_stderr')}`",
            ]
        )
    (out_root / "tsvc_report.md").write_text(
        "\n".join(report_lines) + "\n", encoding="utf-8"
    )

    if status != "pass":
        raise SystemExit(f"error: {error}")

    print(f"ok: TSVC {args.vector_mode} batched artifacts generated under {out_root}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
