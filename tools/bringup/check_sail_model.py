#!/usr/bin/env python3
"""
Validate the Sail model status and active-surface wording for v0.56.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
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
    home = Path.home()
    candidates = sorted(home.glob(".opam/*/bin/sail"))
    if not candidates:
        return None
    return candidates[-1]


def _run_sail_entry(entry_path: Path) -> tuple[bool, str]:
    sail = _find_sail_binary()
    if not sail:
        return False, "sail binary not found"
    cmd = [str(sail), "--just-check", str(entry_path)]
    proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "unknown sail failure").strip()
    return True, f"sail entry parsed with {sail}"


def _check_generated_decode() -> tuple[bool, str]:
    cmd = [sys.executable, "tools/isa/gen_sail_decode.py", "--check"]
    proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "decode generator drift").strip()
    return True, "decode.sail matches generator"


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
    ap = argparse.ArgumentParser(description="Validate Sail model status for canonical v0.56")
    ap.add_argument("--spec", default="isa/v0.56/linxisa-v0.56.json")
    ap.add_argument("--status", default="isa/sail/semantics_status.json")
    ap.add_argument("--entry", default="isa/sail/model/linxisa.sail")
    ap.add_argument("--require-parser", action="store_true", help="Fail if the sail binary is unavailable")
    args = ap.parse_args(argv)

    spec = _read_json(Path(args.spec))
    status = _load_status(Path(args.status))

    instructions = spec.get("instructions")
    if not isinstance(instructions, list):
        raise SystemExit(f"error: malformed spec file: {args.spec}")
    spec_mnemonics = sorted({str(inst.get("mnemonic", "")).strip() for inst in instructions if str(inst.get("mnemonic", "")).strip()})

    if str(status.get("schema_version", "")).strip() != "linx-sail-status-v0.56":
        raise SystemExit("error: semantics_status.schema_version must be 'linx-sail-status-v0.56'")
    mnemonic_statuses = status.get("mnemonics")
    if not isinstance(mnemonic_statuses, dict):
        raise SystemExit("error: semantics_status.mnemonics must be an object")

    resolved: dict[str, str] = {}
    extra_mnemonics = sorted(set(mnemonic_statuses) - set(spec_mnemonics))
    if extra_mnemonics:
        raise SystemExit(f"error: semantics_status contains unknown mnemonics: {extra_mnemonics[:20]}")
    for mnemonic in spec_mnemonics:
        state = str(mnemonic_statuses.get(mnemonic, "")).strip()
        if state not in {"implemented", "stubbed", "unimplemented"}:
            raise SystemExit(f"error: semantics_status.mnemonics[{mnemonic!r}] must be implemented|stubbed|unimplemented")
        resolved[mnemonic] = state

    stubbed = sorted(name for name, state in resolved.items() if state == "stubbed")
    unimplemented = sorted(name for name, state in resolved.items() if state == "unimplemented")

    entry_path = Path(args.entry)
    parser_ok, parser_detail = _run_sail_entry(entry_path)
    if args.require_parser and not parser_ok:
        raise SystemExit(f"error: Sail parser check failed: {parser_detail}")
    decode_ok, decode_detail = _check_generated_decode()

    stale_hits = _collect_stale_hits(
        [
            Path("isa/sail/README.md"),
            Path("isa/sail/model/decode/decode.sail"),
            Path("isa/sail/model/state/state.sail"),
            Path("isa/sail/model/execute/execute.sail"),
            Path("isa/sail/model/linxisa.sail"),
            Path("isa/sail/model/linxisa.sail_project"),
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
    if stubbed:
        failures.append(f"stubbed Sail mnemonics remain: {', '.join(stubbed[:20])}" + (" ..." if len(stubbed) > 20 else ""))
    if unimplemented:
        failures.append(
            f"unimplemented Sail mnemonics remain: {', '.join(unimplemented[:20])}"
            + (" ..." if len(unimplemented) > 20 else "")
        )
    if args.require_parser and not parser_ok:
        failures.append(f"Sail parser check skipped/failed: {parser_detail}")
    if not decode_ok:
        failures.append(f"Sail decode generator check failed: {decode_detail}")

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    parser_summary = parser_detail if parser_ok else f"optional-skip: {parser_detail}"
    print(f"ok: sail model validated (mnemonics={len(spec_mnemonics)}, parser={parser_summary}, decode={decode_detail})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
