#!/usr/bin/env python3
"""
Compatibility wrapper for the tools/model-owned differential suite runner.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


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
    cmd = [
        sys.executable,
        str(runner),
        "--root",
        str(root),
        "--suite",
        args.suite,
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

    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.report_out:
        report_out = Path(args.report_out)
        report_out.parent.mkdir(parents=True, exist_ok=True)
        report_out.write_text(rendered, encoding="utf-8")

    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
