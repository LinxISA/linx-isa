#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ADDR_RE = re.compile(r"^\s*([0-9a-fA-F]+):")
RELOC_RE = re.compile(r"0x([0-9a-fA-F]+)\s+(R_[A-Za-z0-9_]+)\b")
CALL_RE = re.compile(r"\b(?:HL\.)?BSTART(?:\.STD)?\s+CALL,")
ASM_CALL_RE = re.compile(r"\b(?:HL\.|L\.)?BSTART(?:\.STD)?\s+CALL,")

CALL_RELOC_TYPES = {
    "R_LINX_B17_PCREL",
    "R_LINX_B17_PLT",
    "R_LINX_HL_BSTART30_PCREL",
    "R_LinxV5_17_BNEXT",
    "R_LinxV5_48_BNEXT",
    "R_LinxV5_64_BNEXT",
}

SETRET_RELOC_TYPES = {
    "R_LINX_CSETRET5_PCREL",
    "R_LINX_SETRET20_PCREL",
    "R_LINX_HL_SETRET32_PCREL",
    "R_LinxV5_ADDPC",
}


def parse_calls(text: str) -> list[tuple[int, bool, bool, str]]:
    calls: list[tuple[int, bool, bool, str]] = []
    for line in text.splitlines():
        m = ADDR_RE.match(line)
        if not m:
            continue
        if "CALL" not in line or "ICALL" in line or "BSTART" not in line:
            continue
        if not CALL_RE.search(line):
            continue
        off = int(m.group(1), 16)
        is_hl = "HL.BSTART" in line
        has_ra = "ra=" in line
        calls.append((off, is_hl, has_ra, line.strip()))
    return calls


def parse_relocs(text: str) -> dict[int, set[str]]:
    relocs: dict[int, set[str]] = {}
    for line in text.splitlines():
        m = RELOC_RE.search(line)
        if not m:
            continue
        off = int(m.group(1), 16)
        typ = m.group(2)
        relocs.setdefault(off, set()).add(typ)
    return relocs


def parse_asm_calls(text: str) -> list[tuple[int, bool, str]]:
    calls: list[tuple[int, bool, str]] = []
    in_file_scope_inline_asm = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if "Start of file scope inline assembly" in line:
            in_file_scope_inline_asm = True
            continue
        if "End of file scope inline assembly" in line:
            in_file_scope_inline_asm = False
            continue
        if in_file_scope_inline_asm:
            continue
        if "CALL" not in line or "ICALL" in line or "BSTART" not in line:
            continue
        if not ASM_CALL_RE.search(line):
            continue
        calls.append((lineno, "ra=" in line, line.rstrip()))
    return calls


def get_setret_reloc_offset(is_hl: bool, line: str) -> int:
    if is_hl:
        return 6
    if "L.BSTART" in line:
        return 8
    return 4


def has_type(relocs: dict[int, set[str]], off: int, allowed: set[str]) -> bool:
    types = relocs.get(off)
    if not types:
        return False
    return bool(types & allowed)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Verify Linx CALL headers in objects keep call/setret relocations."
    )
    ap.add_argument("--objdump", required=True, help="Path to llvm-objdump disassembly output")
    ap.add_argument("--relocs", required=True, help="Path to llvm-readobj -r output")
    ap.add_argument("--asm", help="Optional generated assembly to verify fused ra= call syntax")
    ap.add_argument("--label", default="", help="Human-readable test label")
    ap.add_argument(
        "--strict-relocs",
        action="store_true",
        help=(
            "Require CALL and SETRET relocations on all CALL headers. "
            "Without this flag, local fused headers without relocations are accepted."
        ),
    )
    args = ap.parse_args(argv)

    objdump_path = Path(args.objdump)
    relocs_path = Path(args.relocs)
    asm_path = Path(args.asm) if args.asm else None

    if not objdump_path.exists():
        print(f"error: missing objdump file: {objdump_path}", file=sys.stderr)
        return 2
    if not relocs_path.exists():
        print(f"error: missing reloc file: {relocs_path}", file=sys.stderr)
        return 2
    if asm_path is not None and not asm_path.exists():
        print(f"error: missing asm file: {asm_path}", file=sys.stderr)
        return 2

    calls = parse_calls(objdump_path.read_text(encoding="utf-8", errors="replace"))
    relocs = parse_relocs(relocs_path.read_text(encoding="utf-8", errors="replace"))
    asm_missing_ra: list[tuple[int, str]] = []
    if asm_path is not None:
        for lineno, has_ra, line in parse_asm_calls(
            asm_path.read_text(encoding="utf-8", errors="replace")
        ):
            if not has_ra:
                asm_missing_ra.append((lineno, line))

    missing_call: list[tuple[int, str]] = []
    missing_setret: list[tuple[int, int, str]] = []

    for off, is_hl, has_ra, line in calls:
        has_call_reloc = has_type(relocs, off, CALL_RELOC_TYPES)
        if args.strict_relocs and not has_call_reloc:
            missing_call.append((off, line))
            continue
        if has_call_reloc:
            setret_off = off + get_setret_reloc_offset(is_hl, line)
            if not has_type(relocs, setret_off, SETRET_RELOC_TYPES):
                missing_setret.append((off, setret_off, line))

    if not asm_missing_ra and not missing_call and not missing_setret:
        return 0

    label = f"[{args.label}] " if args.label else ""
    if asm_missing_ra:
        print(f"error: {label}missing fused ra=... in generated asm CALL headers:", file=sys.stderr)
        for lineno, line in asm_missing_ra[:20]:
            print(f"  {asm_path}:{lineno}: {line}", file=sys.stderr)
        if len(asm_missing_ra) > 20:
            print(f"  ... and {len(asm_missing_ra) - 20} more", file=sys.stderr)
    if missing_call:
        print(f"error: {label}missing CALL relocations:", file=sys.stderr)
        for off, line in missing_call[:20]:
            print(f"  0x{off:x}: {line}", file=sys.stderr)
        if len(missing_call) > 20:
            print(f"  ... and {len(missing_call) - 20} more", file=sys.stderr)
    if missing_setret:
        print(f"error: {label}missing SETRET relocations for fused CALL headers:", file=sys.stderr)
        for call_off, setret_off, line in missing_setret[:20]:
            print(
                f"  call@0x{call_off:x} expected setret reloc at 0x{setret_off:x}: {line}",
                file=sys.stderr,
            )
        if len(missing_setret) > 20:
            print(f"  ... and {len(missing_setret) - 20} more", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
