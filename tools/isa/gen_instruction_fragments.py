#!/usr/bin/env python3
"""Generate per-instruction AsciiDoc fragments under docs/architecture/isa-manual/src/generated/instructions.

This is the include target referenced by the chapter files (e.g. 10_agu.adoc).

Inputs:
  - Compiled spec: isa/v*/linxisa-v*.json
  - Uop classification tree: isa/v*/uop_classification_v*/

Outputs:
  - docs/architecture/isa-manual/src/generated/instructions/*.adoc

Each fragment includes:
  - Syntax (asm)
  - Short description (best-effort)
  - Encoding SVG include
  - Uop classification (big/sub + class payload)
  - Compression kind (if length_bits==16)

NOTE: This is documentation-oriented and should not change the canonical spec.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _mkdirp(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _slug(mnemonic: str) -> str:
    s = mnemonic.strip().lower()
    s = s.replace(".", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "inst"


def _load_uop_class_map(uop_root: Path) -> Dict[str, Dict[str, Any]]:
    """Return mnemonic -> {big_kind, class, group_hint?} map."""
    out: Dict[str, Dict[str, Any]] = {}
    for p in sorted(uop_root.rglob("*.json")):
        if p.name in {"index.json", "_index.json"}:
            continue
        obj = _read_json(p)
        big = str(obj.get("big_kind") or "").strip()
        for it in obj.get("instructions", []) or []:
            m = str(it.get("mnemonic") or "").strip()
            if not m:
                continue
            rec = {
                "big_kind": big,
                "class": it.get("class") or {},
                "group": str(it.get("group") or "").strip(),
            }
            out[m] = rec
    return out


def _uop_group_str(u: Optional[Dict[str, Any]]) -> str:
    if not u:
        return "-"
    big = str(u.get("big_kind") or "").strip() or "-"
    cls = u.get("class") or {}
    # Prefer explicit AGU tuple.
    if big == "AGU":
        agu_kind = str(cls.get("agu_kind") or "").strip()
        addr_mode = str(cls.get("addr_mode") or "").strip()
        if agu_kind and addr_mode:
            return f"{agu_kind}/{addr_mode}"
        if agu_kind:
            return agu_kind
    # Else show uop_kind if present.
    uk = str(cls.get("uop_kind") or "").strip()
    if uk and uk != big:
        return f"{big}/{uk}"
    return big


def _compression_str(length_bits: int, mnemonic: str) -> str:
    if length_bits == 16 or mnemonic.startswith("C."):
        return "C16"
    if length_bits == 48 or mnemonic.startswith("HL."):
        return "HL48"
    if length_bits == 64:
        return "L64"
    return "L32"


def _inst_description(inst: Dict[str, Any]) -> str:
    """Derive a meaningful one-line description from mnemonic, group, and operands.

    Priority: explicit note (JSON) > per-mnemonic table > group + mnemonic heuristics.
    This function must never return a bare \"-\" for any form in the live catalog.
    """
    # 1. JSON catalog carries explicit notes for special/alias forms.
    note = inst.get("note") or ""
    if note.strip():
        return note.strip()

    mnemonic = inst.get("mnemonic") or ""
    group = inst.get("group") or ""
    asm = inst.get("asm") or ""

    # Normalize namespace prefix.
    if mnemonic.startswith("HL."):
        prefix = "HL"
        base = mnemonic[3:]
    elif mnemonic.startswith("C."):
        prefix = "C"
        base = mnemonic[2:]
    elif mnemonic.startswith("V."):
        prefix = "V"
        base = mnemonic[2:]
    else:
        prefix = ""
        base = mnemonic

    # ── Compressed (16-bit) forms ───────────────────────────────────────────
    if prefix == "C":
        if base == "ADD":
            return "Compressed 16-bit register-register addition: Rd = Rs1 + Rs2, result to t."
        if base == "ADDI":
            return "Compressed 16-bit add immediate: Rd = Rs1 + imm, result to t."
        if base == "AND":
            return "Compressed 16-bit bitwise AND: Rd = Rs1 & Rs2, result to t."
        if base == "OR":
            return "Compressed 16-bit bitwise OR: Rd = Rs1 | Rs2, result to t."
        if base == "SUB":
            return "Compressed 16-bit register-register subtraction: Rd = Rs1 - Rs2, result to t."
        if base == "LDI":
            return "Compressed 16-bit load sign-extended immediate into t."
        if base == "LWI":
            return "Compressed 16-bit load 32-bit word from [Rs1+imm] into t."
        if base == "SDI":
            return "Compressed 16-bit store t#1 low 16 bits to [Rs1+imm]."
        if base == "SWI":
            return "Compressed 16-bit store t#1 word to [Rs1+imm]."
        if base == "MOVI":
            return "Compressed 16-bit move sign-extended immediate to register."
        if base == "MOVR":
            return "Compressed 16-bit register move: copy Rs1 to destination."
        if base == "SETRET":
            return "Compressed 16-bit set return address; packs ra with a small uimm offset."
        if base in ("SETC.EQ", "SETC.NE"):
            op = "equal" if base == "SETC.EQ" else "not-equal"
            return f"Compressed 16-bit set condition flag when Rs1 {op} Rs2."
        if base in ("B.DIM", "B.DIMI"):
            op = "load" if "B.DIM" == base else "load immediate"
            return f"Compressed 16-bit block dimension: sets LB0/LB1/LB2 from {op}."
        if base in ("CMP.EQI", "CMP.NEI"):
            op = "equal" if "CMP.EQI" in base else "not-equal"
            return f"Compressed 16-bit compare t#1 {op} immediate, result to t."
        if base == "EBREAK":
            return "Compressed 16-bit breakpoint: raises an EBREAK trap for debugging."
        if base in ("SLLI", "SRLI"):
            op = "logical left" if base == "SLLI" else "logical right"
            return f"Compressed 16-bit {op}-shift of t#1 by uimm bits, result to t."
        if base == "SSRGET":
            return "Compressed 16-bit SSR read: loads the selected SSR into t."
        if base.startswith("BSTART."):
            kind = base.split(".")[1] if "." in base else ""
            br = kind.replace("STD", "standard").replace("SYS", "system")
            if kind in ("MPAR", "MSEQ", "VPAR", "VSEQ"):
                br += " SIMT kernel"
            return f"Compressed 16-bit block start marker: BSTART.{kind} ({br} transition)."
        if base in ("SEXT.B", "SEXT.H", "SEXT.W"):
            sz = {"SEXT.B": "8", "SEXT.H": "16", "SEXT.W": "32"}
            return f"Compressed 16-bit sign-extend Rs1 from {sz[base]}-bit to 64-bit, result to t."
        if base in ("ZEXT.B", "ZEXT.H", "ZEXT.W"):
            sz = {"ZEXT.B": "8", "ZEXT.H": "16", "ZEXT.W": "32"}
            return f"Compressed 16-bit zero-extend Rs1 from {sz[base]}-bit to 64-bit, result to t."
        if base == "SETC.TGT":
            return "Compressed 16-bit set block target register from Rs1."
        # Generic compressed fallback
        return "Compressed 16-bit instruction variant."

    # ── Vector (64-bit V.*) forms ───────────────────────────────────────────
    if prefix == "V":
        if base.startswith("LD.") and ".BRG" not in base:
            width = base[3:].upper()
            return f"Vector load {width} from tile-local address [SrcL+lc0*stride+imm] into Dst."
        if base.startswith("LD.") and ".BRG" in base:
            width = base[3:].split(".")[0].upper()
            return f"Vector load {width} from bridged global address into Dst."
        if base.startswith("SW.") and ".BRG" not in base:
            width = base[3:].upper()
            return f"Vector store {width} to tile-local address from SrcD lane-by-lane."
        if base.startswith("SW.") and ".BRG" in base:
            width = base.split(".")[1].upper()
            return f"Vector store {width} to bridged global address from SrcD lane-by-lane."
        if base in ("ADD", "ADDI", "SUB", "SUBI", "MUL"):
            op = base.upper()
            if "I" in base:
                return f"Vector lane-wise {op} of SrcL with immediate, result to Dst."
            return f"Vector lane-wise {op} of SrcL with SrcR, result to Dst."
        if base in ("AND", "ANDI", "OR", "ORI", "XOR", "XORI"):
            return f"Vector lane-wise bitwise {base[1:].upper()} of operands, result to Dst."
        if base in ("SLL", "SLLI", "SRL", "SRLI", "SRA", "SRAI"):
            dir_ = "left" if "SL" in base else ("right logical" if "SRL" in base else "right arithmetic")
            return f"Vector lane-wise {dir_}-shift of SrcL by SrcR/imm bits, result to Dst."
        if base.startswith("CMP."):
            cond = base[4:].lower()
            if cond.endswith("I"):
                return f"Vector lane-wise compare {cond[:-1]} of SrcL with immediate, write mask to Dst."
            return f"Vector lane-wise compare {cond} of SrcL with SrcR, write mask to Dst."
        if base in ("FADD", "FSUB", "FMUL", "FDIV", "FSQRT"):
            return f"Vector lane-wise floating-point {base[1:].lower()} of operands, result to Dst."
        if base.startswith("FMADD"):
            return "Vector lane-wise fused multiply-add: Dst = ±(SrcL * SrcR) ± SrcA, result to Dst."
        if base.startswith("FMSUB"):
            return "Vector lane-wise fused multiply-subtract: Dst = ±(SrcL * SrcR) ∓ SrcA, result to Dst."
        if base in ("FNMADD", "FNMSUB"):
            neg = "negated-multiply-add" if "FM" in base and "N" in base else base
            return f"Vector lane-wise {neg.lower()} of operands, result to Dst."
        if base.startswith("FMAX") or base.startswith("FMIN"):
            return f"Vector lane-wise floating-point {'max' if 'MAX' in base else 'min'} of SrcL and SrcR, result to Dst."
        if base.startswith("FEQ") or base.startswith("FLT") or base.startswith("FGE") or base.startswith("FNE"):
            cond = base[1:].lower().rstrip("S")
            return f"Vector lane-wise floating-point compare {cond} of SrcL and SrcR, write mask to Dst."
        if base.startswith("RD"):
            red = base[2:].lower()
            return f"Vector lane-wise reduction ({red}) of SrcL across active lanes, scalar result to Dst."
        if base in ("DIV", "REM"):
            return f"Vector lane-wise integer {base.lower()} of SrcL by SrcR, result to Dst."
        if base in ("FABS", "FEXP", "FRECIP", "FCLASS"):
            return f"Vector lane-wise {base[1:].lower()} of SrcL, result to Dst."
        if base.startswith("SHFL."):
            return f"Vector lane-wise shuffle ({base[5:].lower()}) of SrcL, result to Dst."
        if base.startswith("SHFLI."):
            return f"Vector lane-wise indexed shuffle ({base[6:].lower()}) of SrcL, result to Dst."
        if base in ("CSEL", "PSEL"):
            return f"Vector lane-wise conditional select: Dst = SrcP ? SrcL : SrcR."
        if base in ("QPOP", "QPUSH"):
            return f"Vector queue {'pop' if base == 'QPOP' else 'push'} operation on SrcL, result to Dst."
        if base.startswith("LD.AND") or base.startswith("LD.OR") or base.startswith("LD.XOR") or base.startswith("LD.ADD") or base.startswith("LD.MAX") or base.startswith("LD.MIN"):
            atom = base[3:].upper()
            return f"Vector atomic fetch-and-{atom.lower()} {atom} at address [SrcL+SrcR], result to Dst."
        if base.startswith("SW.AND") or base.startswith("SW.OR") or base.startswith("SW.XOR") or base.startswith("SW.ADD") or base.startswith("SW.MAX") or base.startswith("SW.MIN"):
            atom = base[3:].upper()
            return f"Vector atomic store-and-{atom.lower()} {atom} at address [SrcL+SrcR]."
        if base in ("BIC", "BIS", "BXS", "BXU"):
            return f"Vector lane-wise bit {base.lower()} of SrcL controlled by SrcR, result to Dst."
        if base in ("BCNT", "CLZ", "CTZ"):
            return f"Vector lane-wise {base.lower()} of SrcL, result to Dst."
        if base == "REV":
            return "Vector lane-wise bit-reversal of SrcL, result to Dst."
        if base.startswith("FCVT") and "I" not in base:
            return f"Vector lane-wise floating-point format conversion of SrcL, result to Dst."
        if base.startswith("FCVTI") or base.startswith("ICVTF") or base.startswith("ICVT"):
            return f"Vector lane-wise conversion of SrcL, result to Dst."
        if base.startswith("FCLAS"):
            return "Vector lane-wise classify SrcL, write class mask to Dst."
        # Generic vector fallback
        return "Vector instruction (64-bit SIMD lane-by-lane execution)."

    # ── High-level (48-bit HL.*) forms ──────────────────────────────────────
    if prefix == "HL":
        if base.startswith("ADD") or base.startswith("SUB") or base.startswith("AND") or base.startswith("OR") or base.startswith("XOR"):
            op = base[:4].lower()
            w = " (word)" if "W" in base.upper() else ""
            return f"Long 48-bit {op.upper()}{w} with 32-bit immediate, result to Rd/t/u."
        if base.startswith("LUI"):
            return "Long 48-bit load upper immediate (32-bit constant), result to Rd/t/u."
        if base.startswith("LIS"):
            return "Long 48-bit load immediate signed (32-bit sign-extended constant), result to Rd/t/u."
        if base.startswith("LIU"):
            return "Long 48-bit load immediate unsigned (32-bit zero-extended constant), result to Rd/t/u."
        if base.startswith("SETRET"):
            return "Long 48-bit set return address with 32-bit PC-relative offset, packs ra."
        if base.startswith("SETC."):
            cond = base[6:].lower()
            return f"Long 48-bit set condition flag: {cond} of SrcL with operand."
        if base.startswith("CMP."):
            cond = base[4:].lower()
            return f"Long 48-bit compare {cond} with 32-bit immediate, result to Rd/t/u."
        if base.startswith("DIV") or base.startswith("REM") or base.startswith("MUL"):
            w = " (word)" if "W" in base.upper() else ""
            op = base[:3].upper()
            return f"Long 48-bit {op}{w}: Dst0 = quotient, Dst1 = remainder/multiply-high."
        if base.startswith("MADD") or base.startswith("MSUB"):
            w = " (word)" if "W" in base.upper() else ""
            op = "multiply-add" if "MADD" in base else "multiply-sub"
            return f"Long 48-bit {op}{w}: Dst0 = SrcL*SrcR (+/-) SrcD, Dst1 = high part."
        if base.startswith("CCAT"):
            w = " (word)" if "W" in base.upper() else ""
            return f"Long 48-bit barrel-concatenate{w}: Dst0:Dst1 = SrcL:SrcR shifted by shamt bits."
        if base.startswith("BFI"):
            return "Long 48-bit bit-field insert: copy SrcL with bits [M+N-1:M] replaced by SrcR."
        if base.startswith("MIADD") or base.startswith("MISUB"):
            op = "add" if "MIADD" in base else "sub"
            return f"Long 48-bit indexed {op}: Dst = SrcL +/- SrcR*imm, result to Rd/t/u."
        if base.startswith("CAS"):
            width = {"CASB": "byte", "CASH": "halfword", "CASW": "word", "CASD": "doubleword"}
            sz = next((v for k, v in width.items() if base.endswith(k)), "")
            return f"Long 48-bit compare-and-swap {sz} at address [SrcL]: atomically swap with SrcD if SrcR matches."
        if base.startswith("LD.") or base.startswith("LB.") or base.startswith("LH.") or base.startswith("LW."):
            mode = base.split(".")[1] if len(base.split(".")) > 1 else ""
            op = "load" if "L" in base[3] else "store"
            return f"Long 48-bit {op} with PC-relative offset (HL.* PCR) or indexed form (.PO/.PR)."
        if base.startswith("SB.") or base.startswith("SD.") or base.startswith("SH.") or base.startswith("SW."):
            return f"Long 48-bit store with PC-relative offset or indexed form."
        if base.startswith("LBP") or base.startswith("LWP") or base.startswith("LDP") or base.startswith("LHP"):
            return "Long 48-bit load register pair from address [SrcL+offset], results to Dst0 and Dst1."
        if base.startswith("SBIP") or base.startswith("SWIP") or base.startswith("SDIP") or base.startswith("SHIP") or base.startswith("SHP") or base.startswith("SWP") or base.startswith("SDP"):
            return "Long 48-bit store register pair to address [base+offset] from Dst0 and Dst1."
        if base.startswith("PRF") or base.startswith("PRFI"):
            return "Long 48-bit prefetch hint for address [SrcL+SrcR/imm]."
        if base.startswith("QMT"):
            return "Long 48-bit queue management/test:SrcL is a queue tag; result pushed to t/u."
        if base.startswith("QPOP"):
            return "Long 48-bit queue pop: remove head entry from queue SrcL, result to Dst0 and Dst1."
        if base.startswith("QPUSH"):
            return "Long 48-bit queue push: insert SrcL:SrcR into queue, result to t/u."
        if base.startswith("SSRGET"):
            return "Long 48-bit SSR read with extended SSR_ID range, result to Rd/t/u."
        if base.startswith("SSRSET"):
            return "Long 48-bit SSR write: write SrcL to the selected SSR."
        if base.startswith("ADDTPC"):
            return "Long 48-bit add immediate to TPC (temporary PC): TPC = TPC + imm."
        # Generic HL fallback
        return "Long 48-bit instruction encoding (prefix + 32-bit main form)."

    # ── Base (32-bit) forms ──────────────────────────────────────────────────
    group_lower = group.lower()

    # Arithmetic
    if group_lower in ("arithmetic operation 64bit", "arithmetic operation 32bit"):
        op_map = {
            "add": "add", "addw": "add word", "addi": "add immediate",
            "sub": "subtract", "subw": "subtract word", "subi": "subtract immediate",
            "and": "bitwise AND", "andi": "bitwise AND with immediate",
            "or": "bitwise OR", "ori": "bitwise OR with immediate",
            "xor": "bitwise XOR", "xori": "bitwise XOR with immediate",
        }
        key = base[:4].lower()
        if key in op_map:
            w = " (word operation)" if "w" in base.lower() else ""
            return f"{op_map[key].capitalize()}{w}: Rd/t/u = operand1 op operand2."
        if base.startswith("SLL"):
            dir_ = "left" if "SLL" in base else ("right logical" if "SRL" in base else "right arithmetic")
            return f"Shift {dir_} of SrcL by SrcR/shamt bits, result to Rd/t/u."
        return f"{group}: {base} operation."

    # Compare / condition setting
    if group_lower in ("compare instruction", "set commit argument"):
        cond = base.replace(".", " ").lower()
        if base.startswith("CMP."):
            return f"Compare {cond[4:].replace('i',' immediate')}: set Rd/t/u to 1 if true, else 0."
        if base.startswith("SETC."):
            return f"Set block condition flag for {base[6:].lower().replace('i',' immediate')}: consumed by BSTART COND."
        return f"Condition {cond}: set result in Rd/t/u."

    # Load / store
    if any(g in group_lower for g in ("load", "store")):
        op = "Load" if "load" in group_lower else "Store"
        sz_map = {"LB": 8, "LBU": 8, "LH": 16, "LHU": 16, "LW": 32, "LWU": 32, "LD": 64,
                  "SB": 8, "SH": 16, "SW": 32, "SD": 64}
        sz = next((v for k, v in sz_map.items() if base.startswith(k)), 32)
        if "immediate" in group_lower or ".PO" in base or ".PR" in base or ".PCR" in base:
            return f"{op} {sz}-bit {'signed' if 'LB' in base or 'LH' in base or 'LW' in base and 'U' not in base else ''}value {'from' if 'load' in group_lower else 'to'} [Rs+offset], result to Rd/t/u."
        if "pair" in group_lower:
            return f"{op} pair of {sz}-bit values from/to [Rs+offset], results to two destinations."
        if "scaled" not in group_lower and "unscaled" not in group_lower:
            return f"{op} {sz}-bit {'unsigned' if 'U' in base else 'signed'} value {'from' if 'load' in group_lower else 'to'} [Rs+offset], result to Rd/t/u."
        if "scaled" in group_lower or "unscaled" in group_lower or "offset" in group_lower:
            return f"{op} {sz}-bit value {'from' if 'load' in group_lower else 'to'} [Rs+offset], result to Rd/t/u."
        return f"{op} {sz}-bit value {'from' if 'load' in group_lower else 'to'} memory, result to Rd/t/u."

    # Bit ops
    if group_lower in ("bit operation", "bit manipulation"):
        op_map = {
            "clz": "count leading zeros", "ctz": "count trailing zeros", "bcnt": "bit count",
            "rev": "bit-reverse", "bis": "bit select", "bic": "bit inverse select",
            "bxs": "bit extract sign-extend", "bxu": "bit extract zero-extend",
        }
        if base.lower() in op_map:
            return f"{op_map[base.lower()]}: Dst = popcount/extract/select bits of SrcL/M/N, result to Rd/t/u."
        return f"{group}: {base} bit manipulation."

    # Multi-cycle ALU
    if group_lower in ("multi-cycle alu", "division"):
        w = " (word)" if "W" in base.upper() else ""
        if base.startswith("MUL") or base.startswith("MADD"):
            return f"Multiply{w}: Dst = SrcL * SrcR, high part Dst1."
        if base.startswith("DIV"):
            return f"Divide{w}: Dst0 = quotient, Dst1 = remainder."
        if base.startswith("REM"):
            return f"Remainder{w}: Dst0 = remainder, Dst1 = quotient."
        return f"{group}: {base} operation."

    # FP
    if any(g in group_lower for g in ("floating-point", "format convert", "floating point")):
        if base.startswith("FCVT"):
            return f"Floating-point format conversion: convert SrcL to destination format, result to Rd/t/u."
        if base.startswith("SCVTF") or base.startswith("UCVTF"):
            return f"Integer-to-floating-point conversion: convert SrcL to floating-point, result to Rd/t/u."
        if base.startswith("FMADD"):
            return "Floating-point fused multiply-add: Dst = +(SrcL * SrcR) + SrcA."
        if base.startswith("FMSUB"):
            return "Floating-point fused multiply-subtract: Dst = +(SrcL * SrcR) - SrcA."
        if base.startswith("FNMSUB"):
            return "Floating-point negated multiply-subtract: Dst = -(SrcL * SrcR) - SrcA."
        if base.startswith("FNMADD"):
            return "Floating-point negated multiply-add: Dst = -(SrcL * SrcR) + SrcA."
        if any(b in base for b in ("FABS", "FSQRT", "FEXP", "FRECIP")):
            return f"Floating-point {base[1:].lower()}: Dst = {base[1:].lower()}(SrcL)."
        if any(b in base for b in ("FEQ", "FNE", "FLT", "FGE")):
            return f"Floating-point compare {base[1:].lower().rstrip('S')}: set Rd/t/u to 1 if true, else 0."
        if any(b in base for b in ("FMAX", "FMIN")):
            return f"Floating-point {base.lower()} of SrcL and SrcR, result to Rd/t/u."
        return f"{group}: {base} floating-point operation."

    # AMO
    if group_lower in ("atomic operation", "atomic"):
        if base.startswith("LR."):
            w = {"LR.B": "byte", "LR.H": "halfword", "LR.W": "word", "LR.D": "doubleword"}[base]
            return f"Load-reserve {w}: atomically load and set reservation on address [Rs]."
        if base.startswith("SC."):
            w = {"SC.B": "byte", "SC.H": "halfword", "SC.W": "word", "SC.D": "doubleword"}[base]
            return f"Store-conditional {w}: store SrcD to [Rd] if reservation valid."
        if base.startswith("SWAP"):
            w = {"SWAPB": "byte", "SWAPH": "halfword", "SWAPW": "word", "SWAPD": "doubleword"}[base]
            return f"Atomic swap {w}: atomically swap [Rs] with SrcR, result to Rd/t/u."
        if any(base.startswith(p) for p in ("LD.", "LW.", "SD.", "SW.")):
            atom = next(p for p in (".ADD", ".AND", ".OR", ".XOR", ".SMAX", ".SMIN", ".UMAX", ".UMIN") if base.endswith(p))
            op = atom[1:]
            return f"Atomic fetch-and-{op.lower()} {op} at address [Rs+RsR]: old value to Rd/t/u, updated memory."
        return f"Atomic memory operation: {base} at address [Rs+offset]."

    # Block / branch
    if "block" in group_lower or "branch" in group_lower or "split" in group_lower:
        if base == "BSTOP":
            return "Block stop marker: terminates the current block and commits BARG."
        if base == "BSTART":
            return "Block start marker: terminates the current block and begins the next block."
        if base.startswith("BSTART."):
            kind = base[7:].split()[0] if " " in base else base[7:]
            return f"Block start marker: BSTART.{kind} with {group.split()[-1].lower() if ' ' in group else group.lower()} semantics."
        if base.startswith("B.EQ") or base.startswith("B.NE") or base.startswith("B.LT") or base.startswith("B.GE") or base.startswith("B.Z") or base.startswith("B.NZ"):
            return f"Conditional branch: take branch if {base[2:].lower().replace('z','zero').replace('nz','not zero')}."
        if base in ("J",):
            return "Unconditional jump to PC-relative label."
        if base in ("JR",):
            return "Unconditional jump to address in register plus PC-relative offset."
        if base.startswith("FENTRY") or base.startswith("FEXIT") or base.startswith("FRET"):
            return f"Template block {base}: compact prologue/epilogue sequence."
        if base.startswith("MCOPY") or base.startswith("MSET"):
            return f"Memory block {base}: bulk memory fill/copy operation."
        if base.startswith("XB"):
            return "Cross-block call: initiates a block transition with return context."
        return f"Block {group_lower.replace('split','control')}: {base}."

    # System
    if any(g in group_lower for g in ("system", "execution control", "cache", "control", "access")):
        if base == "EBREAK":
            return "Environment breakpoint: raises an EBREAK trap for debugging/halt."
        if base == "ASSERT":
            return "Assertion trap: raises an illegal-instruction trap if SrcL is zero."
        if base.startswith("FENCE"):
            return "Memory fence: orders memory accesses per pred_imm/succ_imm mask."
        if base in ("BWE", "BWI", "BWT", "BSE"):
            return f"Branch barrier/wait: {base} instruction for control-flow speculation management."
        if base in ("ACRE", "ACRC"):
            return "Access control ring transition: request a change in ACR privilege level."
        if base.startswith("SSR") or base.startswith("LSR"):
            return "System register access: read/write system status register."
        if any(base.startswith(p) for p in ("DC.", "IC.", "TLB.", "BC.")):
            return f"Cache/TLB maintenance: {base} operation on the specified memory hierarchy."
        if base.startswith("SETC.TGT"):
            return "Set block target register: BARG.TGT = SrcL, consumed by RET/IND transitions."
        if base.startswith("SETRET"):
            return "Set return address: materialize return address into ra."
        if base.startswith("ADDTPC"):
            return "Add immediate to temporary PC: TPC = TPC + simm."
        return f"System instruction: {base}."

    # Tile / command
    if any(g in group_lower for g in ("tile", "command", "reduce", "shuffle", "move", "concat", "general manager", "general", "immediate", "pc-relative", "compound")):
        if base.startswith("B.IOT"):
            return "Tile input/output descriptor: binds tile operands and allocation metadata to a block."
        if base.startswith("B.IOR"):
            return "GPR input/output descriptor: binds scalar registers to a block argument slot."
        if base.startswith("B.ARG"):
            return "Block argument descriptor: carries layout format and pad policy for TMA operations."
        if base.startswith("B.DIM"):
            return "Block dimension descriptor: sets LB0/LB1/LB2 loop-bound registers."
        if base.startswith("B.TEXT"):
            return "Block text descriptor: selects the out-of-line SIMT kernel body entrypoint."
        if base.startswith("B.HINT"):
            return "Block hint descriptor: carries performance hints (branch likelihood, temperature, prefetch)."
        if base.startswith("B.CATR") or base.startswith("B.DATR"):
            return "Block attribute descriptor: encodes ordering, datatype, layout, and padding hints."
        if base.startswith("RD"):
            red = base[2:].lower()
            return f"Vector reduction ({red}): reduce lane values across active lanes, scalar result to Rd/t/u."
        if base.startswith("SHFL"):
            return f"Vector shuffle ({base.split('.')[1].lower()}): permute lane data within the vector."
        if base.startswith("LUI"):
            return "Load upper immediate: load a 32-bit constant into the upper bits of Rd/t/u."
        if base.startswith("CSEL"):
            return "Conditional select: Rd/t/u = SrcP ? SrcL : SrcR."
        if base.startswith("QMT") or base.startswith("QPOP") or base.startswith("QPUSH"):
            return f"Queue management: {base} operation on queue identified by SrcL."
        if base.startswith("ADDTPC"):
            return "Add to temporary PC: TPC = TPC + simm."
        return f"{group}: {base}."

    # PC-relative / offset
    if "pc-relative" in group_lower:
        if base.startswith("ADDTPC"):
            return "Add signed immediate to TPC: TPC = TPC + simm."
        if base.startswith("SETRET"):
            return "Set return address: materialize return address with PC-relative offset into ra."
        return f"PC-relative operation: {base}."

    # Catch-all: use group + base name.
    return f"{group}: {base} operation."


def _emit_fragment(inst: Dict[str, Any], uop: Optional[Dict[str, Any]], out_dir: Path, enc_rel_dir: str) -> None:
    mnemonic = str(inst.get("mnemonic") or "").strip()
    asm = str(inst.get("asm") or "").strip()
    length_bits = int(inst.get("length_bits") or 0)

    desc = _inst_description(inst)
    uop_group = _uop_group_str(uop)
    comp = _compression_str(length_bits, mnemonic)

    enc_svg = f"enc_{_slug(mnemonic)}.svg"

    anchor = f"inst_{_slug(mnemonic)}"

    lines: List[str] = []
    lines.append("---")
    lines.append("// Auto-generated instruction documentation")
    lines.append("// Do not edit by hand")
    lines.append("")
    lines.append(f"[[{anchor}]]")
    lines.append(f"==== {mnemonic}")
    lines.append("")
    lines.append(f"*Syntax:* {asm}" if asm else "*Syntax:* -")
    lines.append("")
    lines.append(f"*Description:* {desc}")
    lines.append("")
    lines.append("*Encoding:*")
    lines.append("")
    lines.append(f"image::{enc_rel_dir}/{enc_svg}[{mnemonic} encoding,width=800]")
    lines.append("")
    lines.append(f"*Uop-Class:* {uop_group}")
    lines.append("")
    lines.append(f"*Compression:* {comp} (len={length_bits})")

    # Include the raw class dict to make the doc self-contained.
    if uop and uop.get("class"):
        cls = json.dumps(uop["class"], sort_keys=True)
        lines.append("")
        lines.append(f"*Uop-Class payload:* `{cls}`")

    out_path = out_dir / f"{_slug(mnemonic)}.adoc"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _emit_all(spec_path: Path, uop_root: Path, out_dir: Path, enc_rel_dir: str) -> List[str]:
    spec = _read_json(spec_path)
    insts = list(spec.get("instructions", []))

    uop_map = _load_uop_class_map(uop_root)

    _mkdirp(out_dir)
    expected_names: List[str] = []
    for inst in insts:
        m = str(inst.get("mnemonic") or "").strip()
        if not m:
            continue
        expected_names.append(f"{_slug(m)}.adoc")
        uop = uop_map.get(m)
        _emit_fragment(inst, uop, out_dir, enc_rel_dir)
    return sorted(set(expected_names))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--profile",
        choices=["v0.56"],
        default="v0.56",
        help="ISA profile for default --spec and --uop-root paths",
    )
    ap.add_argument("--spec", default=None, help="Path to ISA catalog JSON")
    ap.add_argument("--uop-root", default=None, help="Path to uop classification directory")
    ap.add_argument(
        "--out-dir",
        default="docs/architecture/isa-manual/src/generated/instructions",
        help="Output directory for generated per-instruction fragments",
    )
    ap.add_argument(
        "--enc-rel-dir",
        default="../generated/encodings",
        help="Relative path from instructions/ to encodings/ for image:: includes",
    )
    ap.add_argument("--check", action="store_true", help="Fail if outputs are not up-to-date")
    args = ap.parse_args()

    profile = args.profile
    spec_path = Path(args.spec or f"isa/{profile}/linxisa-{profile}.json")
    uop_root = Path(args.uop_root or f"isa/{profile}/uop_classification_{profile}")
    out_dir = Path(args.out_dir)

    if args.check:
        with tempfile.TemporaryDirectory() as td:
            tmp_out = Path(td)
            expected_names = _emit_all(spec_path, uop_root, tmp_out, args.enc_rel_dir)
            want_names = sorted(p.name for p in out_dir.glob("*.adoc"))
            if want_names != expected_names:
                missing = sorted(set(expected_names) - set(want_names))
                extra = sorted(set(want_names) - set(expected_names))
                if missing:
                    raise SystemExit(
                        f"MISSING {len(missing)} instruction fragments under {out_dir} "
                        f"(first: {missing[0]}; run gen_instruction_fragments.py)"
                    )
                raise SystemExit(
                    f"EXTRA {len(extra)} instruction fragments under {out_dir} "
                    f"(first: {extra[0]}; run gen_instruction_fragments.py)"
                )
            for name in expected_names:
                want = (out_dir / name).read_text(encoding="utf-8")
                got = (tmp_out / name).read_text(encoding="utf-8")
                if want != got:
                    raise SystemExit(
                        f"OUTDATED {out_dir / name} (regenerate with gen_instruction_fragments.py)"
                    )
        print("OK")
        return 0

    _emit_all(spec_path, uop_root, out_dir, args.enc_rel_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
