#!/usr/bin/env python3
"""Run every PTO 0.58.3 CUBE case in an independent full-system boot."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import run_pto_cube_system as single


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _evidence(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pto-kernels-root", required=True)
    parser.add_argument("--tileop-root", required=True)
    parser.add_argument("--sysroot", required=True)
    parser.add_argument("--clang", required=True)
    parser.add_argument("--kernel", required=True)
    parser.add_argument("--linux-source-root", required=True)
    parser.add_argument("--qemu", required=True)
    parser.add_argument("--qemu-source-root", required=True)
    parser.add_argument("--out-root", required=True)
    parser.add_argument("--timeout", type=int, default=single.DEFAULT_TIMEOUT)
    parser.add_argument(
        "--append",
        default="lpj=1000000 loglevel=1 console=ttyS0 kfence.sample_interval=0",
    )
    parser.add_argument("--qemu-guest-errors", action="store_true")
    args = parser.parse_args(argv)

    out_root = Path(args.out_root).expanduser().resolve()
    if out_root.exists() and any(out_root.iterdir()):
        parser.error(f"output root must be absent or empty: {out_root}")
    out_root.mkdir(parents=True, exist_ok=True)

    runner = Path(single.__file__).resolve()
    results: dict[str, Any] = {}
    common = [
        "--pto-kernels-root", args.pto_kernels_root,
        "--tileop-root", args.tileop_root,
        "--sysroot", args.sysroot,
        "--clang", args.clang,
        "--kernel", args.kernel,
        "--linux-source-root", args.linux_source_root,
        "--qemu", args.qemu,
        "--qemu-source-root", args.qemu_source_root,
        "--timeout", str(args.timeout),
        "--append", args.append,
    ]
    if args.qemu_guest_errors:
        common.append("--qemu-guest-errors")

    for case in single.CUBE_CASES:
        case_root = out_root / case
        evidence_dir = case_root / "evidence"
        command = [
            sys.executable,
            str(runner),
            *common,
            "--case", case,
            "--pto-build-output", str(case_root / "build"),
            "--out-dir", str(evidence_dir),
        ]
        completed = subprocess.run(command, check=False)
        summary_path = evidence_dir / "summary.json"
        if not summary_path.is_file():
            results[case] = {"ok": False, "returncode": completed.returncode}
            continue
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        ok = (
            completed.returncode == 0
            and summary.get("selected_cases") == [case]
            and summary.get("result") == {
                "ok": True,
                "classification": "runtime_pass",
            }
        )
        results[case] = {
            "ok": ok,
            "returncode": completed.returncode,
            "classification": summary.get("result", {}).get("classification"),
            "summary": _evidence(summary_path),
            "log": _evidence(evidence_dir / "qemu.log"),
            "expected": summary.get("expected"),
        }

    passed = sum(bool(result.get("ok")) for result in results.values())
    exact_expected = {
        json.dumps(result.get("expected"), sort_keys=True)
        for result in results.values()
        if result.get("expected") is not None
    }
    ok = passed == len(single.CUBE_CASES) and len(exact_expected) == 1
    aggregate = {
        "schema_version": "pto-cube-system-matrix-v1",
        "mode": "fresh-boot-per-case",
        "cases": results,
        "passed": passed,
        "total": len(single.CUBE_CASES),
        "exact_provenance_consistent": len(exact_expected) == 1,
        "result": {"ok": ok, "classification": "runtime_pass" if ok else "runtime_failure"},
    }
    aggregate_path = out_root / "aggregate_summary.json"
    aggregate_path.write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not ok:
        print(f"error: PTO CUBE cold-boot matrix passed {passed}/{len(single.CUBE_CASES)} ({aggregate_path})", file=sys.stderr)
        return 2
    print(f"ok: PTO CUBE cold-boot matrix passed {passed}/{len(single.CUBE_CASES)} ({aggregate_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
