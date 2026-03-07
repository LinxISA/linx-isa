#!/usr/bin/env python3
"""
Validate LinxTrace schema SemVer compatibility wiring across docs and tooling.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _parse_semver(text: str, *, field: str) -> tuple[int, int]:
    m = re.fullmatch(r"\s*(\d+)\.(\d+)\s*", text)
    if not m:
        raise ValueError(f"invalid SemVer for {field}: {text!r}")
    return int(m.group(1)), int(m.group(2))


def _must_match(pattern: str, text: str, *, field: str) -> str:
    m = re.search(pattern, text, flags=re.S)
    if not m:
        raise ValueError(f"missing pattern for {field}")
    return m.group(1)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate LinxTrace SemVer compatibility contracts")
    ap.add_argument("--root", default=".", help="Repository root")
    ap.add_argument("--strict", action="store_true", help="Enable strict policy token checks")
    ap.add_argument("--out", default="", help="Optional JSON report output path")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    errors: list[str] = []

    trace_contract_path = root / "docs/bringup/contracts/trace_schema.md"
    runtime_path = root / "tools/bringup/run_runtime_convergence.sh"
    strict_path = root / "tools/regression/strict_cross_repo.sh"
    validator_path = root / "tools/bringup/validate_trace_schema.py"
    pyc_diff_path = root / "tools/pyCircuit/contrib/linx/flows/tools/run_linx_qemu_vs_pyc.sh"

    for path in [trace_contract_path, runtime_path, strict_path, validator_path, pyc_diff_path]:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(root)}")

    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    trace_contract = trace_contract_path.read_text(encoding="utf-8", errors="replace")
    runtime_text = runtime_path.read_text(encoding="utf-8", errors="replace")
    strict_text = strict_path.read_text(encoding="utf-8", errors="replace")
    validator_text = validator_path.read_text(encoding="utf-8", errors="replace")
    pyc_diff_text = pyc_diff_path.read_text(encoding="utf-8", errors="replace")

    try:
        contract_version = _must_match(r"Version:\s*`(\d+\.\d+)`", trace_contract, field="trace contract version")
        contract_major, contract_minor = _parse_semver(contract_version, field="trace contract version")

        runtime_default = _must_match(
            r'TRACE_SCHEMA_VERSION="\$\{TRACE_SCHEMA_VERSION:-([0-9]+\.[0-9]+)\}"',
            runtime_text,
            field="run_runtime_convergence TRACE_SCHEMA_VERSION default",
        )
        strict_default = _must_match(
            r'\$\{LINX_TRACE_SCHEMA_VERSION:-([0-9]+\.[0-9]+)\}',
            strict_text,
            field="strict_cross_repo LINX_TRACE_SCHEMA_VERSION default",
        )
        validator_expected = _must_match(
            r'--expected-version",\s*default="([0-9]+\.[0-9]+)"',
            validator_text,
            field="validate_trace_schema expected default",
        )
        validator_assume = _must_match(
            r'--assume-trace-version",\s*default="([0-9]+\.[0-9]+)"',
            validator_text,
            field="validate_trace_schema assume default",
        )
        pyc_default = _must_match(
            r'\$\{LINX_TRACE_SCHEMA_VERSION:-([0-9]+\.[0-9]+)\}',
            pyc_diff_text,
            field="run_linx_qemu_vs_pyc schema default",
        )
    except ValueError as exc:
        errors.append(str(exc))
        contract_major, contract_minor = 0, 0
        contract_version = "0.0"
        runtime_default = strict_default = validator_expected = validator_assume = pyc_default = "0.0"

    defaults = {
        "run_runtime_convergence": runtime_default,
        "strict_cross_repo": strict_default,
        "validate_trace_schema_expected": validator_expected,
        "validate_trace_schema_assume": validator_assume,
        "run_linx_qemu_vs_pyc": pyc_default,
    }

    for field, ver in defaults.items():
        try:
            major, minor = _parse_semver(ver, field=field)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if major != contract_major or minor != contract_minor:
            errors.append(
                f"schema default mismatch: {field}={ver} but contract={contract_version}"
            )

    if args.strict:
        required_policy_patterns = {
            "major_mismatch_rule": r"MAJOR`?\s+mismatch is not allowed",
            "minor_forward_rule": r"MINOR`?\s+is forward-compatible",
            "rejection_rule": r"must be rejected",
        }
        for label, pattern in required_policy_patterns.items():
            if not re.search(pattern, trace_contract, flags=re.I):
                errors.append(f"trace schema contract missing policy clause: {label}")

    report = {
        "ok": len(errors) == 0,
        "contract_version": contract_version,
        "defaults": defaults,
        "errors": errors,
    }

    if args.out:
        out_path = (root / args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    print(f"ok: LinxTrace SemVer compatibility checks passed (version={contract_version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
