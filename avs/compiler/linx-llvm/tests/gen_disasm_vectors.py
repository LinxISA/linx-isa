#!/usr/bin/env python3
"""
Generate a single assembly file containing a decode vector for every instruction
encoding in the LinxISA spec.

This is meant for regression:
- Assemble the output as raw bytes in `.text`.
- Disassemble with `llvm-objdump -d` and verify that the LLVM disassembler
  recognizes the full canonical spec without collapsing too many forms onto
  all-zero operands.

The emitted bytes start from each form's `match` value and then seed variable
fields with stable non-zero defaults that respect simple encoding constraints.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


NAMED_VALUES = {
    "ZERO": 0,
    "RA": 1,
}


def _parse_int(s: str) -> int:
    # JSON currently stores `mask`/`match` as hex strings (e.g. "0x50160002").
    return int(str(s), 0)


def _canon_mnemonic(mnem: str) -> str:
    # Spec includes a tiny number of mnemonics with spaces ("BSTART CALL").
    return str(mnem).strip().replace(" ", ".")


def _normalize_length(length_bits: int) -> int:
    return 64 if length_bits == 48 else length_bits


def _field_width(field: dict[str, object]) -> int:
    return sum(int(piece.get("width", 0) or 0) for piece in field.get("pieces", []))


def _default_field_value(field_name: str, width: int, mnemonic: str) -> int:
    lower = field_name.lower()
    upper_mnemonic = mnemonic.upper()
    if width > 5:
        if lower == "regdst":
            value = (4 << 5) | 1  # vt#1
        elif lower == "srcl":
            value = (3 << 5) | 0  # lc0
        elif lower == "srcr":
            value = (1 << 5) | 0 if ".BRG" in upper_mnemonic else ((4 << 5) | 1)
        elif lower == "srcd":
            value = (4 << 5) | 1
        else:
            value = (4 << 5) | 1
    elif lower == "regdst":
        value = 2
    elif lower == "srcl":
        value = 3
    elif lower == "srcr":
        value = 4
    elif lower == "srcd":
        value = 5
    elif lower == "function":
        value = 3
    elif lower == "tileopcode":
        value = 1
    elif lower == "loopnest":
        value = 1
    elif lower == "brtype":
        value = 1
    elif "imm" in lower or "offset" in lower or "shamt" in lower:
        value = 1
    elif lower in {"c", "l"}:
        value = 1
    else:
        value = 1
    if width <= 0:
        return 0
    return min(value, (1 << width) - 1)


def _apply_constraints(field_name: str, value: int, width: int, constraints: list[dict[str, object]]) -> int:
    max_value = (1 << width) - 1 if width > 0 else 0
    chosen = value
    for constraint in constraints:
        if str(constraint.get("field", "")) != field_name:
            continue
        op = str(constraint.get("op", ""))
        raw = str(constraint.get("value", "0"))
        rhs = NAMED_VALUES.get(raw, int(raw, 0) if raw.isdigit() or raw.startswith("0x") else 0)
        if op == "!=" and chosen == rhs:
            chosen = min(rhs + 1, max_value)
        elif op == ">=" and chosen < rhs:
            chosen = min(rhs, max_value)
    return chosen


def _insert_field_value(word: int, field: dict[str, object], value: int, part_offset_bits: int) -> int:
    for piece in field.get("pieces", []):
        width = int(piece.get("width", 0) or 0)
        if width <= 0:
            continue
        lsb = int(piece.get("insn_lsb", 0) or 0) + part_offset_bits
        mask = ((1 << width) - 1) << lsb
        value_lsb = int(piece.get("value_lsb", 0) or 0)
        piece_value = (value >> value_lsb) & ((1 << width) - 1)
        word = (word & ~mask) | (piece_value << lsb)
    return word


def _seed_instruction_bits(inst: dict[str, object], length_bits: int, parts: list[dict[str, object]]) -> int:
    norm_length = _normalize_length(length_bits)
    if norm_length == 64 and len(parts) == 2 and length_bits == 64:
        word = (_parse_int(parts[1].get("match", "0")) << 32) | _parse_int(parts[0].get("match", "0"))
    else:
        word = _parse_int(parts[0].get("match", "0"))

    constraints = []
    for part in parts:
        constraints.extend(list(part.get("constraints", [])))

    for part in parts:
        part_offset_bits = int(part.get("index", 0) or 0) * 32
        for field in part.get("fields", []):
            width = _field_width(field)
            if width <= 0:
                continue
            name = str(field.get("name", ""))
            value = _default_field_value(name, width, str(inst.get("mnemonic", "")))
            value = _apply_constraints(name, value, width, constraints)
            word = _insert_field_value(word, field, value, part_offset_bits)

    return word & ((1 << norm_length) - 1)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", type=Path, required=True, help="Path to compiled ISA catalog JSON (for example isa/v0.56/linxisa-v0.56.json)")
    ap.add_argument("--out", type=Path, required=True, help="Output assembly file")
    args = ap.parse_args(argv)

    raw = json.loads(args.spec.read_text())
    instructions = raw.get("instructions", [])

    out: list[str] = []
    out.append(f"# Auto-generated from {args.spec}")
    out.append("# DO NOT EDIT BY HAND")
    out.append("")
    out.append("    .text")
    out.append("    .p2align 1")
    out.append("    .globl linxisa_decode_vectors")
    out.append("linxisa_decode_vectors:")

    for inst in instructions:
        inst_id = str(inst.get("id", "")).strip()
        mnem = _canon_mnemonic(inst.get("mnemonic", ""))
        enc = inst.get("encoding", {})
        length_bits = int(enc.get("length_bits", inst.get("length_bits", 0)) or 0)
        parts = list(enc.get("parts", []))

        if length_bits not in (16, 32, 48, 64) or not parts:
            continue

        out.append(f"    # {mnem} ({inst_id}) [{length_bits}]")

        val = _seed_instruction_bits(inst, length_bits, parts)

        if length_bits == 16:
            val &= 0xFFFF
            out.append(f"    .2byte 0x{val:04x}")
        elif length_bits == 32:
            val &= 0xFFFFFFFF
            out.append(f"    .4byte 0x{val:08x}")
        elif length_bits == 48:
            val &= ((1 << 48) - 1)
            lo = val & 0xFFFFFFFF
            hi = (val >> 32) & 0xFFFF
            out.append(f"    .4byte 0x{lo:08x}")
            out.append(f"    .2byte 0x{hi:04x}")
        elif length_bits == 64:
            lo = val & 0xFFFFFFFF
            hi = (val >> 32) & 0xFFFFFFFF
            out.append(f"    .4byte 0x{lo:08x}")
            out.append(f"    .4byte 0x{hi:08x}")

        out.append("")

    out.append("    .p2align 1")
    out.append("linxisa_decode_vectors_end:")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
