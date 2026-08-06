#!/usr/bin/env python3
"""
Validate the Sail model status and active-surface wording for v0.58.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


STALE_PATTERNS = (
    re.compile(r"\bskeleton\b", re.IGNORECASE),
    re.compile(r"\bv0\.4-draft\b", re.IGNORECASE),
)

FORBIDDEN_IMPL_PATTERNS = (
    re.compile(r"\blinx_unimplemented\("),
    re.compile(r"\bvfp_unimpl\b"),
    re.compile(r"\bvrd_unimpl\b"),
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_status(path: Path) -> dict[str, Any]:
    data = _read_json(path)
    if not isinstance(data, dict):
        raise SystemExit(f"error: expected JSON object in {path}")
    return data


def _find_sail_binary() -> Path | None:
    direct = shutil.which("sail")
    if direct:
        return Path(direct)
    return None


def _run_sail_entry(entry_path: Path, expected_version: str) -> tuple[bool, str]:
    sail = _find_sail_binary()
    if not sail:
        return False, "sail binary not found"
    version_proc = subprocess.run(
        [str(sail), "--version"], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    version_text = (version_proc.stdout or version_proc.stderr or "").strip()
    match = re.search(r"\bSail\s+([0-9]+(?:\.[0-9]+)+)\b", version_text)
    if version_proc.returncode != 0 or not match:
        return False, f"could not determine Sail version from {sail}: {version_text!r}"
    if match.group(1) != expected_version:
        return False, f"Sail version {match.group(1)} does not match pinned {expected_version} ({sail})"
    with tempfile.TemporaryDirectory(prefix="linx-sail-z3-") as cache_dir:
        cmd = [
            str(sail),
            "--memo-z3-path",
            str(Path(cache_dir) / "memo"),
            "--just-check",
            str(entry_path),
        ]
        proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "unknown sail failure").strip()
    return True, f"Sail {expected_version} entry parsed with {sail}"


def _run_sail_c_backend(entry_path: Path) -> tuple[bool, str]:
    sail = _find_sail_binary()
    if not sail:
        return False, "sail binary not found"
    with tempfile.TemporaryDirectory(prefix="linx-sail-c-") as tmp:
        output = Path(tmp) / "linxisa"
        proc = subprocess.run(
            [
                str(sail),
                "--memo-z3-path",
                str(Path(tmp) / "z3-memo"),
                "-c",
                "-o",
                str(output),
                str(entry_path),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if proc.returncode != 0:
            return False, (proc.stderr or proc.stdout or "unknown Sail C backend failure").strip()
        if not output.with_suffix(".c").is_file() or not output.with_suffix(".h").is_file():
            return False, "Sail C backend did not produce both .c and .h outputs"
    return True, "Sail C backend generated successfully"


def _run_sail_directed_tests(test_path: Path, expected_version: str) -> tuple[bool, str]:
    sail = _find_sail_binary()
    if not sail:
        return False, "sail binary not found"
    version_proc = subprocess.run(
        [str(sail), "--version"], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    version_text = (version_proc.stdout or version_proc.stderr or "").strip()
    match = re.search(r"\bSail\s+([0-9]+(?:\.[0-9]+)+)\b", version_text)
    if version_proc.returncode != 0 or not match or match.group(1) != expected_version:
        return False, f"directed tests require Sail {expected_version}: {version_text!r}"
    with tempfile.TemporaryDirectory(prefix="linx-sail-directed-") as cache_dir:
        proc = subprocess.run(
            [
                str(sail),
                "--memo-z3-path",
                str(Path(cache_dir) / "z3-memo"),
                "--no-color",
                "--no-warn",
                "-i",
                str(test_path),
            ],
            input="main()\n:run\n",
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    output = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        return False, output.strip() or "Sail interpreter failed"
    if "assert(false" in output or "Assertion failed" in output:
        return False, output.strip()
    if "Result = ()" not in output:
        return False, "Sail interpreter did not report successful main() execution"
    return True, f"directed semantic tests executed with Sail {expected_version}"


def _check_generated_decode(spec_path: Path) -> tuple[bool, str]:
    cmd = [sys.executable, "tools/isa/gen_sail_decode.py", "--spec", str(spec_path), "--check"]
    proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "decode generator drift").strip()
    return True, "decode.sail matches generator"


def _check_generated_status(spec_path: Path) -> tuple[bool, str]:
    cmd = [sys.executable, "tools/isa/gen_sail_status.py", "--spec", str(spec_path), "--check"]
    proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "semantic status generator drift").strip()
    return True, "semantics_status.json matches form-ID policy"


def _check_coverage(spec_path: Path) -> tuple[bool, str]:
    cmd = [sys.executable, "tools/isa/sail_coverage.py", "--spec", str(spec_path), "--check"]
    proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "Sail coverage drift").strip()
    return True, "coverage.json matches semantic status"


def _collect_stale_hits(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in STALE_PATTERNS:
            for idx, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    hits.append(f"{path}:{idx}: stale wording {pattern.pattern!r}")
    return hits


def _collect_impl_gap_hits(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            for pattern in FORBIDDEN_IMPL_PATTERNS:
                if pattern.search(line):
                    hits.append(f"{path}:{idx}: forbidden implementation placeholder {pattern.pattern!r}")
    return hits


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate Sail model status for canonical v0.58")
    ap.add_argument("--spec", default="isa/v0.58/linxisa-v0.58.json")
    ap.add_argument("--status", default="isa/sail/semantics_status.json")
    ap.add_argument("--entry", default="isa/sail/model/linxisa.sail")
    ap.add_argument("--toolchain", default="isa/sail/toolchain.json")
    ap.add_argument("--directed-tests", default="isa/sail/tests/directed.sail")
    ap.add_argument("--require-parser", action="store_true", help="Fail if the sail binary is unavailable")
    ap.add_argument("--require-c-backend", action="store_true", help="Require Sail C backend generation")
    args = ap.parse_args(argv)

    spec_path = Path(args.spec)
    spec = _read_json(spec_path)
    status = _load_status(Path(args.status))
    toolchain = _load_status(Path(args.toolchain))
    expected_sail_version = str(toolchain.get("sail_version") or "").strip()
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)+", expected_sail_version):
        raise SystemExit(f"error: malformed sail_version in {args.toolchain}")

    instructions = spec.get("instructions")
    if not isinstance(instructions, list):
        raise SystemExit(f"error: malformed spec file: {args.spec}")
    release = str(spec.get("version") or "").strip()
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)+", release):
        raise SystemExit(f"error: malformed ISA release in {args.spec}")
    expected_status_schema = f"linx-sail-status-v{release}"
    if str(status.get("schema_version", "")).strip() != expected_status_schema:
        raise SystemExit(
            "error: semantics_status.schema_version must be "
            f"{expected_status_schema!r}"
        )
    form_statuses = status.get("forms")
    if not isinstance(form_statuses, dict):
        raise SystemExit("error: semantics_status.forms must be an object")
    canonical_forms = {str(inst.get("id") or ""): inst for inst in instructions}
    missing_forms = sorted(set(canonical_forms) - set(form_statuses))
    extra_forms = sorted(set(form_statuses) - set(canonical_forms))
    if missing_forms or extra_forms:
        raise SystemExit(f"error: semantics_status form mismatch: missing={missing_forms[:20]} extra={extra_forms[:20]}")
    grade_counts = {grade: 0 for grade in ("decode-only", "executable-subset", "architecturally-complete")}
    for form_id, inst in canonical_forms.items():
        entry = form_statuses[form_id]
        if not isinstance(entry, dict):
            raise SystemExit(f"error: semantics_status.forms[{form_id!r}] must be an object")
        mnemonic = str(inst.get("mnemonic") or "")
        if str(entry.get("mnemonic") or "") != mnemonic:
            raise SystemExit(f"error: semantics_status.forms[{form_id!r}] mnemonic does not match {mnemonic}")
        grade = str(entry.get("status") or "")
        if grade not in grade_counts:
            raise SystemExit(f"error: invalid semantic grade {grade!r} for {form_id}")
        grade_counts[grade] += 1

    entry_path = Path(args.entry)
    parser_ok, parser_detail = _run_sail_entry(entry_path, expected_sail_version)
    decode_ok, decode_detail = _check_generated_decode(spec_path)
    status_ok, status_detail = _check_generated_status(spec_path)
    coverage_ok, coverage_detail = _check_coverage(spec_path)
    c_backend_ok, c_backend_detail = _run_sail_c_backend(entry_path) if args.require_c_backend else (True, "optional-skip")
    directed_ok, directed_detail = _run_sail_directed_tests(Path(args.directed_tests), expected_sail_version)

    stale_hits = _collect_stale_hits(
        [
            Path("isa/sail/README.md"),
            Path("isa/sail/model/decode/decode.sail"),
            Path("isa/sail/model/state/state.sail"),
            Path("isa/sail/model/execute/execute.sail"),
            Path("isa/sail/model/linxisa.sail"),
            Path("isa/sail/model/linxisa.sail_project"),
            Path(args.directed_tests),
        ]
    )
    impl_gap_hits = _collect_impl_gap_hits(
        [
            Path("isa/sail/model/decode/decode.sail"),
            Path("isa/sail/model/state/state.sail"),
            Path("isa/sail/model/execute/execute.sail"),
        ]
    )

    failures: list[str] = []
    if stale_hits:
        failures.extend(stale_hits)
    if impl_gap_hits:
        failures.extend(impl_gap_hits)
    if args.require_parser and not parser_ok:
        failures.append(f"Sail parser check failed: {parser_detail}")
    if not decode_ok:
        failures.append(f"Sail decode generator check failed: {decode_detail}")
    if not status_ok:
        failures.append(f"Sail semantic status generator check failed: {status_detail}")
    if not coverage_ok:
        failures.append(f"Sail coverage check failed: {coverage_detail}")
    if not c_backend_ok:
        failures.append(f"Sail C backend check failed: {c_backend_detail}")
    directed_unavailable = directed_detail.startswith("sail binary not found") or directed_detail.startswith(
        "directed tests require Sail "
    )
    if not directed_ok and (args.require_parser or not directed_unavailable):
        failures.append(f"Sail directed semantic tests failed: {directed_detail}")

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    parser_summary = parser_detail if parser_ok else f"optional-skip: {parser_detail}"
    print(
        "ok: sail model validated "
        f"(forms={len(canonical_forms)}, grades={grade_counts}, parser={parser_summary}, "
        f"decode={decode_detail}, status={status_detail}, directed={directed_detail}, "
        f"coverage={coverage_detail}, c_backend={c_backend_detail})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
