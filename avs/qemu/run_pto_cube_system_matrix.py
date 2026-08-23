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


def _canonical_expected() -> dict[str, str]:
    return {
        "pto_kernels": single.PTO_KERNELS_COMMIT,
        "tileop": single.TILEOP_COMMIT,
        "llvm": single.LLVM_COMMIT,
        "qemu": single.QEMU_COMMIT,
        "linux": single.LINUX_COMMIT,
    }


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


def _valid_evidence(record: Any) -> bool:
    if not isinstance(record, dict):
        return False
    try:
        path = Path(record["path"])
        return (
            path.is_file()
            and record["size_bytes"] == path.stat().st_size
            and isinstance(record["sha256"], str)
            and len(record["sha256"]) == 64
            and record["sha256"] == _sha256(path)
        )
    except (KeyError, OSError, TypeError):
        return False


def _provenance_matches_expected(provenance: dict[str, Any],
                                 expected: dict[str, Any]) -> bool:
    source_tool = provenance.get("source_tool")
    if not isinstance(source_tool, dict):
        return False
    for component in ("pto_kernels", "tileop", "linux", "qemu"):
        record = source_tool.get(component)
        if not isinstance(record, dict) or record.get("expected_commit") != expected.get(component):
            return False
    clang = source_tool.get("clang")
    return isinstance(clang, dict) and clang.get("expected_commit") == expected.get("llvm")


def _validate_source_tool_provenance(provenance: Any) -> bool:
    if not isinstance(provenance, dict):
        return False
    expected = _canonical_expected()
    try:
        for component, allow_same_tree in (
            ("pto_kernels", False), ("tileop", False),
            ("linux", True), ("qemu", True),
        ):
            recorded = provenance[component]
            fresh = single._require_git_identity(
                Path(recorded["path"]), expected[component],
                allow_same_tree=allow_same_tree,
            )
            if recorded != fresh:
                return False
        if provenance["clang"] != single._require_tool_commit(
            Path(provenance["clang"]["path"]), expected["llvm"]
        ):
            return False
        for component in ("kernel", "qemu_binary"):
            if provenance[component] != single._file_evidence(
                Path(provenance[component]["path"])
            ):
                return False
        pto_lock = provenance["pto_lock"]
        if not _valid_evidence(pto_lock.get("file")):
            return False
        if pto_lock.get("identity") != {
            "release": single.PTO_RELEASE,
            "encoding_projection_sha256": single.PTO_PROJECTION,
            "content_sha256": single.PTO_CONTENT,
        }:
            return False
    except (KeyError, OSError, TypeError, single.GateError, subprocess.CalledProcessError):
        return False
    return True


def _aggregate_results(results: dict[str, Any]) -> dict[str, Any]:
    required_cases = set(single.CUBE_CASES)
    exact_case_keys = set(results) == required_cases
    rows_valid = True
    validated_passed = 0
    expected_values: set[str] = set()
    provenance_values: set[str] = set()

    for case in single.CUBE_CASES:
        row = results.get(case)
        if not isinstance(row, dict):
            rows_valid = False
            continue
        expected = row.get("expected")
        provenance = row.get("provenance")
        row_valid = (
            row.get("ok") is True
            and row.get("returncode") == 0
            and row.get("classification") == "runtime_pass"
            and row.get("selected_cases") == [case]
            and isinstance(expected, dict)
            and expected == _canonical_expected()
            and isinstance(provenance, dict)
            and _valid_evidence(row.get("summary"))
            and _valid_evidence(row.get("log"))
        )
        if row_valid:
            row_valid = _provenance_matches_expected(provenance, expected)
        if row_valid:
            validated_passed += 1
        rows_valid &= row_valid
        if isinstance(expected, dict):
            expected_values.add(json.dumps(expected, sort_keys=True))
        if isinstance(provenance, dict):
            provenance_values.add(json.dumps(provenance, sort_keys=True))

    canonical_expected_json = json.dumps(_canonical_expected(), sort_keys=True)
    expected_consistent = (
        len(expected_values) == 1
        and next(iter(expected_values)) == canonical_expected_json
        and len(results) == len(required_cases)
    )
    provenance_consistent = len(provenance_values) == 1 and len(results) == len(required_cases)
    expected_fingerprint = (
        hashlib.sha256(next(iter(expected_values)).encode("utf-8")).hexdigest()
        if expected_consistent else None
    )
    provenance_fingerprint = (
        hashlib.sha256(next(iter(provenance_values)).encode("utf-8")).hexdigest()
        if provenance_consistent else None
    )
    passed = validated_passed
    ok = exact_case_keys and rows_valid and expected_consistent and provenance_consistent
    return {
        "schema_version": "pto-cube-system-matrix-v1",
        "mode": "fresh-boot-per-case",
        "cases": results,
        "passed": passed,
        "total": len(single.CUBE_CASES),
        "exact_case_keys": exact_case_keys,
        "expected_consistent": expected_consistent,
        "actual_provenance_consistent": provenance_consistent,
        "expected_fingerprint_sha256": expected_fingerprint,
        "actual_provenance_fingerprint_sha256": provenance_fingerprint,
        "result": {"ok": ok, "classification": "runtime_pass" if ok else "runtime_failure"},
    }


def _load_case_result(case: str, evidence_dir: Path, returncode: int) -> dict[str, Any]:
    summary_path = evidence_dir / "summary.json"
    log_path = evidence_dir / "qemu.log"
    if not summary_path.is_file() or not log_path.is_file():
        return {"ok": False, "returncode": returncode}
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    ok = (
        returncode == 0
        and summary.get("selected_cases") == [case]
        and summary.get("result") == {
            "ok": True,
            "classification": "runtime_pass",
        }
    )
    pto_identity = summary.get("pto_identity")
    identity_files = pto_identity.get("files", {}) if isinstance(pto_identity, dict) else {}
    identity_parser = pto_identity.get("parser") if isinstance(pto_identity, dict) else None
    libc_record = identity_files.get("libc.so")
    loader_record = identity_files.get("ld-musl-linx64.so.1")
    runtime_provenance = {
        "source_tool": summary.get("provenance"),
        "libc_sha256": libc_record.get("sha256") if isinstance(libc_record, dict) else None,
        "loader_sha256": loader_record.get("sha256") if isinstance(loader_record, dict) else None,
        "identity_parser_sha256": (
            identity_parser.get("sha256") if isinstance(identity_parser, dict) else None
        ),
        "needed": summary.get("needed"),
    }
    if (
        not isinstance(runtime_provenance["source_tool"], dict)
        or not _validate_source_tool_provenance(runtime_provenance["source_tool"])
        or not _valid_evidence(libc_record)
        or not _valid_evidence(loader_record)
        or not _valid_evidence(identity_parser)
        or not all(
            isinstance(runtime_provenance[key], str) and len(runtime_provenance[key]) == 64
            for key in ("libc_sha256", "loader_sha256", "identity_parser_sha256")
        )
        or not isinstance(runtime_provenance["needed"], dict)
    ):
        runtime_provenance = None
    return {
        "ok": ok,
        "returncode": returncode,
        "classification": summary.get("result", {}).get("classification"),
        "selected_cases": summary.get("selected_cases"),
        "summary": _evidence(summary_path),
        "log": _evidence(log_path),
        "expected": summary.get("expected"),
        "provenance": runtime_provenance,
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
    parser.add_argument(
        "--reaggregate-existing",
        action="store_true",
        help="revalidate existing per-case summaries without launching QEMU",
    )
    args = parser.parse_args(argv)

    out_root = Path(args.out_root).expanduser().resolve()
    if args.reaggregate_existing and not out_root.is_dir():
        parser.error(f"existing output root not found: {out_root}")
    if not args.reaggregate_existing and out_root.exists() and any(out_root.iterdir()):
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
        returncode = 0
        if not args.reaggregate_existing:
            command = [
                sys.executable,
                str(runner),
                *common,
                "--case", case,
                "--pto-build-output", str(case_root / "build"),
                "--out-dir", str(evidence_dir),
            ]
            returncode = subprocess.run(command, check=False).returncode
        results[case] = _load_case_result(case, evidence_dir, returncode)

    aggregate = _aggregate_results(results)
    ok = aggregate["result"]["ok"]
    passed = aggregate["passed"]
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
