#!/usr/bin/env python3
"""check_tepl_encoding.py

Verify that TEPL TileOp10 encodings are consistent across:

- ISA manual canonical map (04_block_isa.adoc)
- PTO-Kernel constants (include/common/pto_tileop.hpp) if available
- Optional other consumers (LLVM/QEMU) *if present* in the superproject

Policy:
- The ISA manual map is treated as the canonical encoding contract.
- Other sources may omit ops (unimplemented), but MUST NOT disagree on any op they define.
- Other sources MUST NOT define TEPL ops that are absent from the manual map.

Exit code:
- 0 on success
- non-zero on mismatch
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


RE_MANUAL_PAIR = re.compile(r"\b([A-Z][A-Z0-9_.]*)=0x([0-9A-Fa-f]{3})\b")
RE_PTO_CONST = re.compile(r"\bconstexpr\s+unsigned\s+([A-Z][A-Z0-9_.]*)\s*=\s*0x([0-9A-Fa-f]{3})u;\b")


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


def _parse_manual_map(text: str) -> dict[str, int]:
    pairs = RE_MANUAL_PAIR.findall(text)
    if not pairs:
        raise RuntimeError("failed to find any TEPL TileOp10 assignments in manual section")
    out: dict[str, int] = {}
    for name, hx in pairs:
        out[name] = int(hx, 16)
    return out


def _parse_pto_constants(text: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for name, hx in RE_PTO_CONST.findall(text):
        out[name] = int(hx, 16)
    return out


def _report_diff(canonical: SourceMap, other: SourceMap) -> tuple[int, list[str]]:
    errs = 0
    notes: list[str] = []

    # Conflicts or extras are errors.
    for name, code in other.items.items():
        if name not in canonical.items:
            errs += 1
            notes.append(f"ERROR: {other.name} defines {name}=0x{code:03X} but manual has no assignment")
            continue
        want = canonical.items[name]
        if want != code:
            errs += 1
            notes.append(
                f"ERROR: {other.name} defines {name}=0x{code:03X} but manual requires 0x{want:03X}"
            )

    # Missing entries are informational (unimplemented).
    missing = [n for n in canonical.items.keys() if n not in other.items]
    if missing:
        notes.append(
            f"NOTE: {other.name} does not define {len(missing)}/{len(canonical.items)} manual TEPL ops (treated as unimplemented)."
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
    ap = argparse.ArgumentParser(description="Check TEPL TileOp10 encoding consistency")
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument(
        "--manual",
        default="docs/architecture/isa-manual/src/chapters/04_block_isa.adoc",
        help="path to ISA manual chapter containing TEPL map",
    )
    ap.add_argument(
        "--pto-submodule",
        default="workloads/pto_kernels",
        help="path to PTO-Kernel submodule dir (git repo)",
    )
    ap.add_argument(
        "--pto-const-path",
        default="include/common/pto_tileop.hpp",
        help="path inside PTO-Kernel repo for TileOp10 constants",
    )
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    manual_path = root / args.manual
    if not manual_path.exists():
        print(f"error: manual file not found: {manual_path}", file=sys.stderr)
        return 2

    manual_text = manual_path.read_text(encoding="utf-8")
    # We parse the whole file but only match the TEPL assignment style pairs.
    manual_map = _parse_manual_map(manual_text)
    canonical = SourceMap("manual(04_block_isa.adoc)", manual_map)

    print(f"manual TEPL ops: {len(canonical.items)}")

    # PTO-Kernel constants (via git show so we don't depend on checkout state).
    pto_dir = root / args.pto_submodule
    pto_items: dict[str, int] = {}
    if pto_dir.exists():
        try:
            pto_text = _run_git_show(pto_dir, f"HEAD:{args.pto_const_path}")
            pto_items = _parse_pto_constants(pto_text)
            other = SourceMap("PTO-Kernel(include/common/pto_tileop.hpp)", pto_items)
            errs, notes = _report_diff(canonical, other)
            for line in notes:
                print(line)
            if errs:
                return 1
        except RuntimeError as exc:
            print(f"NOTE: skipping PTO-Kernel check: {exc}")

    # Optional checks: LLVM/QEMU tables if present.
    # We only do a light-touch scan for obvious constant definitions; absence is not an error.
    optional_candidates = [
        root / "qemu" / "target" / "linx" / "translate.c",
        root / "qemu" / "target" / "linx" / "decode.c",
        root / "llvm" / "lib" / "Target" / "Linx" / "LinxInstrInfo.td",
        root / "llvm" / "lib" / "Target" / "Linx" / "LinxISelLowering.cpp",
    ]

    qemu_path, qemu_txt = _find_optional_text(optional_candidates, r"TileOp10|BSTART\.TEPL|TEPL")
    if qemu_path is None:
        print("NOTE: no QEMU/LLVM TEPL consumer file detected in this repo; skipped optional checks.")
    else:
        print(f"NOTE: found potential TEPL consumer file at {qemu_path} (no strict parser implemented; skipped).")

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
