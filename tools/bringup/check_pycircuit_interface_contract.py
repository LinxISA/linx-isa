#!/usr/bin/env python3
"""
Validate pyCircuit <-> LinxCore interface contract and producer wiring.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any


def _parse_semver(ver: str, *, field: str) -> tuple[int, int]:
    m = re.fullmatch(r"\s*(\d+)\.(\d+)\s*", ver)
    if not m:
        raise ValueError(f"invalid SemVer for {field}: {ver!r}")
    return int(m.group(1)), int(m.group(2))


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"contract JSON must decode to object: {path}")
    return data


def _extract_python_list(path: Path, var_name: str) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == var_name:
                value = ast.literal_eval(node.value)
                if not isinstance(value, list):
                    raise ValueError(f"{path}: {var_name} is not a list")
                out: list[str] = []
                for item in value:
                    if not isinstance(item, str):
                        raise ValueError(f"{path}: {var_name} contains non-string entry")
                    out.append(item)
                return out
    raise ValueError(f"{path}: missing list variable {var_name}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate pyCircuit interface contract")
    ap.add_argument("--root", default=".", help="Repository root")
    ap.add_argument("--strict", action="store_true", help="Enable strict compatibility checks")
    ap.add_argument("--out", default="", help="Optional JSON report path")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    errors: list[str] = []

    contract_path = root / "docs/bringup/contracts/pyc_linxcore_interface_contract.json"
    contract_md_path = root / "docs/bringup/contracts/pyc_linxcore_interface_contract.md"
    trace_validator_path = root / "tools/bringup/validate_trace_schema.py"

    if not contract_path.is_file():
        errors.append(f"missing contract file: {contract_path.relative_to(root)}")
    if not contract_md_path.is_file():
        errors.append(f"missing contract markdown: {contract_md_path.relative_to(root)}")
    if not trace_validator_path.is_file():
        errors.append(f"missing trace validator: {trace_validator_path.relative_to(root)}")

    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    try:
        contract = _load_json(contract_path)
    except Exception as exc:
        print(f"error: failed to parse contract JSON: {exc}", file=sys.stderr)
        return 1

    version = str(contract.get("version", "")).strip()
    trace_schema_version = str(contract.get("trace_schema_version", "")).strip()
    required_commit_fields = contract.get("required_commit_fields")
    required_env = contract.get("required_env")
    producer_scripts = contract.get("producer_scripts")

    try:
        _parse_semver(version, field="contract version")
    except ValueError as exc:
        errors.append(str(exc))

    try:
        _parse_semver(trace_schema_version, field="trace_schema_version")
    except ValueError as exc:
        errors.append(str(exc))

    if not isinstance(required_commit_fields, list) or not required_commit_fields:
        errors.append("required_commit_fields must be a non-empty list")
    if not isinstance(required_env, list) or not required_env:
        errors.append("required_env must be a non-empty list")
    if not isinstance(producer_scripts, list) or not producer_scripts:
        errors.append("producer_scripts must be a non-empty list")

    required_commit_fields_norm: list[str] = []
    if isinstance(required_commit_fields, list):
        for field in required_commit_fields:
            if not isinstance(field, str) or not field.strip():
                errors.append(f"invalid required_commit_fields entry: {field!r}")
                continue
            required_commit_fields_norm.append(field.strip())

    producer_paths: list[Path] = []
    if isinstance(producer_scripts, list):
        for rel in producer_scripts:
            if not isinstance(rel, str) or not rel.strip():
                errors.append(f"invalid producer_scripts entry: {rel!r}")
                continue
            path = (root / rel).resolve()
            producer_paths.append(path)
            if not path.is_file():
                errors.append(f"missing producer script: {rel}")

    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    try:
        diff_fields = _extract_python_list(
            root / "tools/pyCircuit/contrib/linx/flows/tools/linx_trace_diff.py",
            "MANDATORY_FIELDS",
        )
        validator_fields = _extract_python_list(trace_validator_path, "DEFAULT_REQUIRED_FIELDS")
    except Exception as exc:
        print(f"error: failed to parse required field lists: {exc}", file=sys.stderr)
        return 1

    for field in diff_fields:
        if field not in required_commit_fields_norm:
            errors.append(f"contract missing linx_trace_diff mandatory field: {field}")
    for field in validator_fields:
        if field not in required_commit_fields_norm:
            errors.append(f"contract missing validate_trace_schema required field: {field}")

    run_cpp_path = root / "tools/pyCircuit/contrib/linx/flows/tools/run_linx_cpu_pyc_cpp.sh"
    run_diff_path = root / "tools/pyCircuit/contrib/linx/flows/tools/run_linx_qemu_vs_pyc.sh"
    run_cpp = run_cpp_path.read_text(encoding="utf-8", errors="replace")
    run_diff = run_diff_path.read_text(encoding="utf-8", errors="replace")

    env_required_in_cpp = {"PYC_COMMIT_TRACE", "PYC_BOOT_PC", "PYC_MEM_BYTES", "PYC_MAX_CYCLES"}
    for key in env_required_in_cpp:
        if key not in run_cpp:
            errors.append(f"run_linx_cpu_pyc_cpp.sh missing expected env token: {key}")

    if "validate_trace_schema.py" not in run_diff:
        errors.append("run_linx_qemu_vs_pyc.sh missing validate_trace_schema.py call")
    if "linx_trace_diff.py" not in run_diff:
        errors.append("run_linx_qemu_vs_pyc.sh missing linx_trace_diff.py call")

    if args.strict:
        md_text = contract_md_path.read_text(encoding="utf-8", errors="replace")
        strict_tokens = [
            "Breaking interface changes require `MAJOR` bump",
            "Additive backward-compatible changes require `MINOR` bump",
            "Unversioned interface breaks are rejected",
        ]
        for token in strict_tokens:
            if token not in md_text:
                errors.append(f"contract markdown missing strict policy token: {token}")

    report = {
        "ok": len(errors) == 0,
        "contract_version": version,
        "trace_schema_version": trace_schema_version,
        "required_commit_fields_count": len(required_commit_fields_norm),
        "producer_scripts": [str(p.relative_to(root)) for p in producer_paths],
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

    print(f"ok: pyCircuit interface contract checks passed (version={version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
