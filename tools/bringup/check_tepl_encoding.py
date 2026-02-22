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


def _parse_manual_map(text: str) -> dict[str, int]:
    # The manual includes non-canonical legacy notes later in the file; we must
    # scope parsing to the canonical map section only.
    start_marker = "Strict-v0.3 TEPL `TileOp10` assignment (current canonical map):"
    end_marker = "Non-canonical legacy note:"

    start = text.find(start_marker)
    if start < 0:
        raise RuntimeError(f"failed to locate TEPL canonical map start marker: {start_marker!r}")
    end = text.find(end_marker, start)
    if end < 0:
        raise RuntimeError(f"failed to locate TEPL canonical map end marker: {end_marker!r}")

    section = text[start:end]

    pairs = RE_MANUAL_PAIR.findall(section)
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


def _parse_qemu_tepl_constants(text: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for raw_name, hx in RE_QEMU_TEPL_CONST.findall(text):
        # QEMU uses C identifiers; map to manual token style.
        name = raw_name.replace("_", ".")
        out[name] = int(hx, 16)
    return out


def _parse_llvm_tepl_tileop_cases(text: str) -> dict[str, int]:
    """
    Parse LLVM TEPL TileOp10 keyword table.

    We intentionally scope this to the `parseTEPLTileOpKeyword` helper so we
    don't accidentally treat other `.Case(...)` tables as TEPL encodings.
    """

    # Best-effort slice to the TEPL table to avoid false positives.
    marker = "parseTEPLTileOpKeyword"
    i = text.find(marker)
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

    # Optional checks: LLVM/QEMU consumers in the superproject if present.
    qemu_consumer = root / "emulator" / "qemu" / "target" / "linx" / "helper.c"
    if qemu_consumer.exists():
        qemu_items = _parse_qemu_tepl_constants(qemu_consumer.read_text(encoding="utf-8", errors="ignore"))
        if qemu_items:
            other = SourceMap(f"QEMU({qemu_consumer.relative_to(root)})", qemu_items)
            errs, notes = _report_diff(canonical, other)
            for line in notes:
                print(line)
            if errs:
                return 1
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
            if errs:
                return 1
        else:
            print(f"NOTE: LLVM TEPL consumer present but no tileop cases parsed: {llvm_consumer}")
    else:
        print("NOTE: no LLVM TEPL consumer file detected under compiler/llvm; skipped optional check.")

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
