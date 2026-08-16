#!/usr/bin/env python3
"""
Compatibility wrapper for the tools/model-owned differential suite runner.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from itertools import combinations
from pathlib import Path


class ReleaseStrictError(ValueError):
    """A differential report lacks release-promotion evidence."""


def _require_release_strict(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseStrictError(message)


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def validate_release_strict_payload(payload: dict) -> None:
    cases = payload.get("cases")
    _require_release_strict(
        isinstance(cases, list) and bool(cases),
        "release-strict requires at least one differential case",
    )
    for case in cases:
        case_id = str(case.get("id", "<unknown>")) if isinstance(case, dict) else "<unknown>"
        provenance = (
            case.get("provenance", payload.get("provenance"))
            if isinstance(case, dict)
            else payload.get("provenance")
        )
        _require_release_strict(
            isinstance(provenance, dict),
            "release-strict requires immutable artifact provenance",
        )
        artifacts = provenance.get("artifacts") if isinstance(provenance, dict) else None
        _require_release_strict(
            isinstance(artifacts, dict),
            "release-strict requires immutable artifact provenance",
        )
        for name in ("compiler", "linker", "elf", "qemu", "model", "manifest", "golden"):
            row = artifacts.get(name) if isinstance(artifacts, dict) else None
            _require_release_strict(
                isinstance(row, dict)
                and isinstance(row.get("path"), str)
                and bool(row["path"])
                and _is_sha256(row.get("sha256")),
                f"release-strict provenance missing path/SHA-256 for {name}",
            )
        _require_release_strict(
            provenance.get("verified_after_run") is True,
            "release-strict provenance was not re-verified after the run",
        )
        _require_release_strict(
            isinstance(case, dict) and case.get("status") == "pass",
            f"release-strict case {case_id} did not pass",
        )
        result_memory = case.get("result_memory")
        _require_release_strict(
            isinstance(result_memory, dict) and len(result_memory) >= 2,
            f"release-strict case {case_id} lacks independent result memory",
        )
        model_names = sorted(result_memory)
        for model_name in model_names:
            row = result_memory.get(model_name)
            _require_release_strict(
                isinstance(row, dict)
                and isinstance(row.get("path"), str)
                and bool(row["path"])
                and _is_sha256(row.get("sha256")),
                f"release-strict case {case_id} has incomplete {model_name} result memory",
            )

        golden = case.get("golden_comparisons")
        _require_release_strict(
            isinstance(golden, dict)
            and all(
                isinstance(golden.get(name), dict)
                and golden[name].get("status") == "pass"
                for name in model_names
            ),
            f"release-strict case {case_id} lacks passing independent golden comparisons",
        )
        pairwise = case.get("pairwise_comparisons")
        expected_pairs = [
            (f"{left}:{right}", f"{right}:{left}")
            for left, right in combinations(model_names, 2)
        ]
        _require_release_strict(
            isinstance(pairwise, dict)
            and all(
                any(
                    isinstance(pairwise.get(pair), dict)
                    and pairwise[pair].get("status") == "pass"
                    for pair in orientations
                )
                for orientations in expected_pairs
            ),
            f"release-strict case {case_id} lacks passing pairwise comparisons",
        )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Compatibility wrapper for the tools/model differential suite")
    ap.add_argument("--root", default="")
    ap.add_argument("--suite", default="avs/model/linx_model_diff_suite.yaml")
    ap.add_argument("--workdir", default="")
    ap.add_argument("--profile", default="", help="Compatibility-only metadata field.")
    ap.add_argument("--trace-schema-version", default="", help="Compatibility-only metadata field.")
    ap.add_argument("--report-out", default="", help="Optional path to write the JSON summary.")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]
    runner = root / "tools" / "model" / "tests" / "avs" / "run_model_diff_suite.py"

    env = dict(os.environ)
    env["LINX_VIRT_TEST_FINISHER"] = "1"
    cmd = [
        sys.executable,
        str(runner),
        "--root",
        str(root),
        "--suite",
        args.suite,
        "--qemu",
        str(root / "emulator" / "qemu" / "build-linx" / "qemu-system-linx64"),
        "--qemu-bios",
        "none",
    ]
    if args.workdir:
        cmd.extend(["--workdir", args.workdir])

    proc = subprocess.run(
        cmd,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    if proc.returncode != 0:
        sys.stdout.write(proc.stdout)
        return proc.returncode

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.stdout.write(proc.stdout)
        return proc.returncode

    if args.profile:
        payload["profile"] = args.profile
    if args.trace_schema_version:
        payload["trace_schema_version"] = args.trace_schema_version

    if args.profile == "release-strict":
        if args.trace_schema_version != "1.0":
            print("error: release-strict requires --trace-schema-version 1.0", file=sys.stderr)
            return 2
        try:
            validate_release_strict_payload(payload)
        except ReleaseStrictError as exc:
            payload["release_strict"] = {"status": "fail", "error": str(exc)}
            rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
            if args.report_out:
                report_out = Path(args.report_out)
                report_out.parent.mkdir(parents=True, exist_ok=True)
                report_out.write_text(rendered, encoding="utf-8")
            sys.stdout.write(rendered)
            return 1
        payload["release_strict"] = {"status": "pass"}

    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.report_out:
        report_out = Path(args.report_out)
        report_out.parent.mkdir(parents=True, exist_ok=True)
        report_out.write_text(rendered, encoding="utf-8")

    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
