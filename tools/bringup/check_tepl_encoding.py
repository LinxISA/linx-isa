#!/usr/bin/env python3
"""check_tepl_encoding.py

Verify that TEPL tile opcode encodings are consistent across:

- ISA canonical engine-op catalog (`isa/v0.4/state/engine_ops.json`)
- PTO-Kernel constants (include/common/pto_tileop.hpp) if available
- Optional other consumers (LLVM/QEMU) *if present* in the superproject

Policy:
- The v0.4 engine-op catalog is treated as the canonical encoding contract.
- Other sources may omit ops (unimplemented), but MUST NOT disagree on any op they define.
- Other sources MUST NOT define TEPL ops that are absent from the canonical catalog.

Exit code:
- 0 on success
- non-zero on mismatch
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


RE_MANUAL_PAIR = re.compile(r"\b([A-Z][A-Z0-9_.]*)=0x([0-9A-Fa-f]{3})\b")
RE_PTO_CONST = re.compile(
    r"\bconstexpr\s+(?:unsigned|uint32_t)\s+([A-Z][A-Z0-9_.]*)\s*=\s*0x([0-9A-Fa-f]{3})u;"
)
RE_QEMU_TEPL_CONST = re.compile(r"\bLINX_TEPL_([A-Z0-9_]+)\s*=\s*0x([0-9A-Fa-f]{3})u\b")
RE_LLVM_TEPL_CASE = re.compile(r'\.Case\("([A-Z][A-Z0-9_.]*)",\s*0x([0-9A-Fa-f]{3})u\)')


@dataclass(frozen=True)
class SourceMap:
    name: str
    items: dict[str, int]


def _run_git_show(repo_dir: Path, spec: str) -> str:
    proc = subprocess.run(
        ["git", "show", spec],
        cwd=str(repo_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git show failed in {repo_dir}: {spec}\n{proc.stderr.strip()}")
    return proc.stdout


def _load_engine_ops_map(path: Path) -> dict[str, int]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    tepl = obj.get("tepl")
    if not isinstance(tepl, dict):
        raise RuntimeError(f"{path}: missing top-level tepl object")
    ops = tepl.get("ops")
    if not isinstance(ops, list):
        raise RuntimeError(f"{path}: tepl.ops must be a list")

    out: dict[str, int] = {}
    for idx, op in enumerate(ops):
        if not isinstance(op, dict):
            raise RuntimeError(f"{path}: tepl.ops[{idx}] must be an object")
        name = op.get("name")
        if not isinstance(name, str) or not name.strip():
            raise RuntimeError(f"{path}: tepl.ops[{idx}] missing non-empty name")
        raw = op.get("tile_opcode")
        if isinstance(raw, int):
            selector = raw
        elif isinstance(raw, str):
            selector = int(raw.strip(), 0)
        else:
            raise RuntimeError(f"{path}: tepl.ops[{idx}] missing tile_opcode")
        out[name.strip()] = selector
    return out


def _read_worktree_or_git(repo_dir: Path, rel_path: str) -> str:
    worktree_path = repo_dir / rel_path
    if worktree_path.is_file():
        return worktree_path.read_text(encoding="utf-8", errors="ignore")
    return _run_git_show(repo_dir, f"HEAD:{rel_path}")


def _parse_pto_constants(text: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for name, hx in RE_PTO_CONST.findall(text):
        out[name] = int(hx, 16)
    return out


def _parse_qemu_tepl_constants(text: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for raw_name, hx in RE_QEMU_TEPL_CONST.findall(text):
        # QEMU uses C identifiers; map to manual token style.
        name = raw_name.replace("_", ".")
        out[name] = int(hx, 16)
    return out


def _parse_llvm_tepl_tileop_cases(text: str) -> dict[str, int]:
    """
    Parse LLVM TEPL tile opcode keyword table.

    We intentionally scope this to the `parseTEPLTileOpKeyword` helper so we
    don't accidentally treat other `.Case(...)` tables as TEPL encodings.
    """

    # Best-effort slice to the TEPL table to avoid false positives.
    marker_candidates = ("parseTEPLTileOpcodeKeyword", "parseTEPLTileOpKeyword")
    i = -1
    for marker in marker_candidates:
        i = text.find(marker)
        if i >= 0:
            break
    if i < 0:
        return {}
    window = text[i : i + 16_384]  # enough to cover the full switch table
    out: dict[str, int] = {}
    for name, hx in RE_LLVM_TEPL_CASE.findall(window):
        out[name] = int(hx, 16)
    return out


def _report_diff(canonical: SourceMap, other: SourceMap) -> tuple[int, list[str]]:
    errs = 0
    notes: list[str] = []

    # Conflicts or extras are errors.
    for name, code in other.items.items():
        if name not in canonical.items:
            errs += 1
            notes.append(f"ERROR: {other.name} defines {name}=0x{code:03X} but canonical catalog has no assignment")
            continue
        want = canonical.items[name]
        if want != code:
            errs += 1
            notes.append(
                f"ERROR: {other.name} defines {name}=0x{code:03X} but canonical catalog requires 0x{want:03X}"
            )

    # Missing entries are informational (unimplemented).
    missing = [n for n in canonical.items.keys() if n not in other.items]
    if missing:
        notes.append(
            f"NOTE: {other.name} does not define {len(missing)}/{len(canonical.items)} canonical TEPL ops (treated as unimplemented)."
        )
    return errs, notes


def _find_optional_text(paths: Iterable[Path], pattern: str) -> tuple[Path | None, str | None]:
    rx = re.compile(pattern)
    for p in paths:
        if not p.exists() or not p.is_file():
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if rx.search(txt):
            return p, txt
    return None, None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Check TEPL tile opcode encoding consistency")
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument(
        "--engine-ops",
        default="isa/v0.4/state/engine_ops.json",
        help="path to canonical v0.4 TEPL engine-op catalog",
    )
    ap.add_argument(
        "--pto-submodule",
        default="workloads/pto_kernels",
        help="path to PTO-Kernel submodule dir (git repo)",
    )
    ap.add_argument(
        "--pto-const-path",
        default="include/common/pto_tileop.hpp",
        help="path inside PTO-Kernel repo for tile opcode constants",
    )
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    engine_ops_path = root / args.engine_ops
    if not engine_ops_path.exists():
        print(f"error: engine-op catalog not found: {engine_ops_path}", file=sys.stderr)
        return 2

    canonical_map = _load_engine_ops_map(engine_ops_path)
    canonical = SourceMap(f"engine_ops({engine_ops_path.relative_to(root)})", canonical_map)

    print(f"canonical TEPL ops: {len(canonical.items)}")

    total_errs = 0

    # PTO-Kernel constants (prefer working tree; fall back to git HEAD if absent).
    pto_dir = root / args.pto_submodule
    pto_items: dict[str, int] = {}
    if pto_dir.exists():
        try:
            pto_text = _read_worktree_or_git(pto_dir, args.pto_const_path)
            pto_items = _parse_pto_constants(pto_text)
            other = SourceMap("PTO-Kernel(include/common/pto_tileop.hpp)", pto_items)
            errs, notes = _report_diff(canonical, other)
            for line in notes:
                print(line)
            total_errs += errs
        except RuntimeError as exc:
            print(f"NOTE: skipping PTO-Kernel check: {exc}")

    # Optional checks: LLVM/QEMU consumers in the superproject if present.
    qemu_consumer = root / "emulator" / "qemu" / "target" / "linx" / "helper.c"
    if qemu_consumer.exists():
        qemu_items = _parse_qemu_tepl_constants(qemu_consumer.read_text(encoding="utf-8", errors="ignore"))
        if qemu_items:
            other = SourceMap(f"QEMU({qemu_consumer.relative_to(root)})", qemu_items)
            errs, notes = _report_diff(canonical, other)
            for line in notes:
                print(line)
            total_errs += errs
        else:
            print(f"NOTE: QEMU TEPL consumer present but no constants parsed: {qemu_consumer}")
    else:
        print("NOTE: no QEMU TEPL consumer file detected under emulator/qemu; skipped optional check.")

    llvm_consumer = (
        root
        / "compiler"
        / "llvm"
        / "llvm"
        / "lib"
        / "Target"
        / "LinxISA"
        / "AsmParser"
        / "LinxISAAsmParser.cpp"
    )
    if llvm_consumer.exists():
        llvm_items = _parse_llvm_tepl_tileop_cases(
            llvm_consumer.read_text(encoding="utf-8", errors="ignore")
        )
        if llvm_items:
            other = SourceMap(f"LLVM({llvm_consumer.relative_to(root)})", llvm_items)
            errs, notes = _report_diff(canonical, other)
            for line in notes:
                print(line)
            total_errs += errs
        else:
            print(f"NOTE: LLVM TEPL consumer present but no tileop cases parsed: {llvm_consumer}")
    else:
        print("NOTE: no LLVM TEPL consumer file detected under compiler/llvm; skipped optional check.")

    if total_errs:
        print(f"FAIL: detected {total_errs} TEPL tile opcode mismatches", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
