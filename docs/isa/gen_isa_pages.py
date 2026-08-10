#!/usr/bin/env python3
"""
Generate MkDocs-compatible instruction reference pages for LinxISA v0.58.

Creates:
  docs/isa/index.md              — ISA instruction reference hub
  docs/isa/encoding.md           — Encoding formats overview
  docs/isa/groups/index.md        — Instruction group index
  docs/isa/groups/*.md           — Per-group pages (all active groups)
  docs/isa/instructions/index.md — Master instruction index (all canonical forms)
  docs/isa/instructions/*.md     — Per-instruction detail pages

Each instruction page embeds the WaveDrom SVG encoding diagram and includes:
  - Assembly syntax
  - Group / chapter reference
  - Bit-length and decode format tag
  - Semantic description (derived from catalog)
  - Pseudocode (derived from catalog)
  - Encoding notes from catalog
  - Cross-reference to the full ISA manual chapter

Usage:
    python3 gen_isa_pages.py \\
        --spec isa/v0.58/linxisa-v0.58.json \\
        --out-dir docs/isa \\
        --svg-dir docs/isa/wavedrom \\
        --verbose
"""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import re
import sys
import tempfile
from collections import OrderedDict
from typing import Any


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _slug(s: str) -> str:
    """URL-safe slug: keep alphanumeric, collapse dots/spaces to underscore."""
    s = re.sub(r"\.+", "_", s.strip().lower())
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_") or "x"


def _encoding_asset_filename(inst: dict, mnemonic_count: int) -> str:
    """Mirror the canonical form-aware naming contract in gen_encoding_svg.py."""
    if mnemonic_count > 1:
        form_id = str(inst.get("id") or "").strip()
        if not re.fullmatch(r"[a-z0-9_]+", form_id):
            raise ValueError(
                f"instruction {inst.get('mnemonic')!r} has an invalid stable form ID {form_id!r}"
            )
        return f"enc_{form_id}.svg"
    suffix = "_parts" if len(inst.get("parts", [])) > 1 else ""
    return f"enc_{_slug(str(inst['mnemonic']))}{suffix}.svg"


def _esc(s: str) -> str:
    """Escape special MkDocs/markdown characters."""
    return re.sub(r"([*_`#>])", r"\\\1", s)


def _collapse_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# ─────────────────────────────────────────────────────────────────────────────
# Chapter mapping — maps catalog groups to manual chapters
# ─────────────────────────────────────────────────────────────────────────────

# Canonical group → (manual_chapter_num, manual_chapter_title)
# These correspond to the active LinxISA v0.58 manual chapters.
MANUAL_CHAPTERS: dict[str, tuple[int, str]] = {
    "Arithmetic":                     (12, "ALU — Arithmetic Logic Unit"),
    "Arithmetic Operation":           (12, "ALU — Arithmetic Logic Unit"),
    "Arithmetic Operation 32bit":     (12, "ALU — Arithmetic Logic Unit"),
    "Arithmetic Operation 64bit":    (12, "ALU — Arithmetic Logic Unit"),
    "Bit Operation":                 (12, "ALU — Arithmetic Logic Unit"),
    "Bit Manipulation":              (12, "ALU — Arithmetic Logic Unit"),
    "Compare Instruction":           (16, "BRU — Branch and Compare"),
    "Max-Min":                      (16, "BRU — Branch and Compare"),
    "Compound Operation":            (12, "ALU — Arithmetic Logic Unit"),
    "Multi-Cycle ALU":              (12, "ALU — Arithmetic Logic Unit"),
    "Immediate":                     (12, "ALU — Arithmetic Logic Unit"),
    "PC-Relative":                  (16, "BRU — Branch and Compare"),
    "RESERVE":                      (18, "RSV — Reserved and Indexed Operations"),
    "Concat":                       (18, "RSV — Reserved and Indexed Operations"),
    "Long Immediate":                (12, "ALU — Arithmetic Logic Unit"),
    # Memory
    "Load Register Offset":          (11, "AGU — Address Generation Unit"),
    "Load Immediate Offset":         (11, "AGU — Address Generation Unit"),
    "Load UnScaled":                (11, "AGU — Address Generation Unit"),
    "Load PC-Relative":             (11, "AGU — Address Generation Unit"),
    "Load Long Offset":             (11, "AGU — Address Generation Unit"),
    "Load Pair":                    (11, "AGU — Address Generation Unit"),
    "Load Post-Index":              (11, "AGU — Address Generation Unit"),
    "Load Pre-Index":               (11, "AGU — Address Generation Unit"),
    "Load Symbol":                  (11, "AGU — Address Generation Unit"),
    "Store Register Offset":         (11, "AGU — Address Generation Unit"),
    "Store Immediate Offset":        (11, "AGU — Address Generation Unit"),
    "Store PC-Relative":            (11, "AGU — Address Generation Unit"),
    "Store Long Offset":            (11, "AGU — Address Generation Unit"),
    "Store Pair":                  (11, "AGU — Address Generation Unit"),
    "Store Post-Index":             (11, "AGU — Address Generation Unit"),
    "Store Pre-Index":              (11, "AGU — Address Generation Unit"),
    "Store Symbol":                 (11, "AGU — Address Generation Unit"),
    "Prefetch":                     (11, "AGU — Address Generation Unit"),
    "Store Offset":                 (11, "AGU — Address Generation Unit"),
    # Floating-point
    "Floating-point Arithmetic":     (13, "FSU — Floating-point / SIMD Unit"),
    "Floating Point Arithmetic":     (20, "VEC — Vector / SIMD Execution (lx64)"),
    "Floating-point Compare":        (13, "FSU — Floating-point / SIMD Unit"),
    "Format Convert":               (13, "FSU — Floating-point / SIMD Unit"),
    "Two-Source Floating Point":     (20, "VEC — Vector / SIMD Execution (lx64)"),
    "Three-Source Floating Point":   (20, "VEC — Vector / SIMD Execution (lx64)"),
    # Atomic
    "Atomic Operation":              (14, "AMO — Atomic Memory Operations"),
    "Atomic":                       (14, "AMO — Atomic Memory Operations"),
    # Block ISA
    "Block Split":                  (4,  "Block ISA — Block-structured Control Flow"),
    "BSTART":                       (4,  "Block ISA — Block-structured Control Flow"),
    "Branch":                       (16, "BRU — Branch and Compare"),
    "Set Commit Argument":           (16, "BRU — Branch and Compare"),
    "C.BSTART":                     (15, "BBD — Block Boundary Delimiters"),
    "Block Argument":               (4,  "Block ISA — Block-structured Control Flow"),
    "Block Control Attribute":       (17, "CMD — Command and Control"),
    "Block Data Attribute":          (17, "CMD — Command and Control"),
    "Block Dimension":              (4,  "Block ISA — Block-structured Control Flow"),
    "Block Hint":                    (17, "CMD — Command and Control"),
    "Block Input & Output":          (4,  "Block ISA — Block-structured Control Flow"),
    "Block Offset":                  (4,  "Block ISA — Block-structured Control Flow"),
    "C.UNARY":                      (12, "ALU — Arithmetic Logic Unit"),
    "C.TINST":                      (19, "SYS — System Operations"),
    "Move":                         (12, "ALU — Arithmetic Logic Unit"),
    # Vector
    "Reduce Operation with Register":(20, "VEC — Vector / SIMD Execution (lx64)"),
    "Shuffle":                      (20, "VEC — Vector / SIMD Execution (lx64)"),
    "General Manager":              (20, "VEC — Vector / SIMD Execution (lx64)"),
    "Three Source Integer":         (20, "VEC — Vector / SIMD Execution (lx64)"),
    "Division":                     (20, "VEC — Vector / SIMD Execution (lx64)"),
    # System
    "Execution Control":             (19, "SYS — System Operations"),
    "Cache Maintain":               (19, "SYS — System Operations"),
    "SSR Access":                   (19, "SYS — System Operations"),
    "General Manager":               (9,  "Memory Operations — Loads, Stores, and Atomics"),
    "General":                      (4,  "Block ISA — Block-structured Control Flow"),
}

# Manual chapter index (ordered list for navigation)
MANUAL_CHAPTER_INDEX: list[tuple[int, str, str]] = [
    (3,  "03", "Encoding Formats",                "isa/encoding.md"),
    (4,  "04", "Block ISA",                       "isa/groups/block_split.md"),
    (11, "11", "AGU — Address Generation",        "isa/groups/load_register_offset.md"),
    (12, "12", "ALU — Arithmetic Logic Unit",       "isa/groups/arithmetic.md"),
    (13, "13", "FSU — Floating-point / SIMD",      "isa/groups/floating_point_arithmetic.md"),
    (14, "14", "AMO — Atomic Memory Operations",   "isa/groups/atomic.md"),
    (15, "15", "BBD — Block Boundary Delimiters",   "isa/groups/c_bstart.md"),
    (16, "16", "BRU — Branch and Compare",         "isa/groups/branch.md"),
    (17, "17", "CMD — Command and Control",        "isa/groups/block_control_attribute.md"),
    (18, "18", "RSV — Reserved Operations",        "isa/groups/reserve.md"),
    (19, "19", "SYS — System Operations",          "isa/groups/execution_control.md"),
    (20, "20", "VEC — Vector / SIMD Execution",    "isa/groups/shuffle.md"),
]


def get_manual_chapter(group: str) -> tuple[int, str] | None:
    """Return (chapter_num, chapter_title) for a catalog group, or None."""
    return MANUAL_CHAPTERS.get(group)


def get_chapter_anchor(chapter_num: int) -> str:
    anchors = {
        3: "ch_encoding",
        4: "ch_blockisa",
        11: "ch_agu",
        12: "ch_alu",
        13: "ch_fsu",
        14: "ch_amo",
        15: "ch_bbd",
        16: "ch_bru",
        17: "ch_cmd",
        18: "ch_rsv",
        19: "ch_sys",
        20: "ch_vec",
    }
    return anchors.get(chapter_num, f"chapter_{chapter_num}")


# ─────────────────────────────────────────────────────────────────────────────
# Catalog analysis
# ─────────────────────────────────────────────────────────────────────────────

def _group_instructions(instructions: list[dict]) -> OrderedDict[str, list[dict]]:
    groups: OrderedDict[str, list[dict]] = OrderedDict()
    for inst in instructions:
        g = str(inst.get("group") or "").strip()
        if not g:
            g = "Ungrouped"
        groups.setdefault(g, []).append(inst)
    return groups


def _mnemonic_core(mnemonic: str) -> tuple[str, str, list[str]]:
    """Split mnemonic into (prefix, core, parts)."""
    m = mnemonic.strip()
    enc = ""
    for p in ("C.", "HL.", "V."):
        if m.startswith(p):
            enc = p[:-1]
            m = m[len(p):]
            break
    core = m.strip()
    parts = [x for x in core.replace(" ", ".").split(".") if x]
    return enc, core, parts


# ─────────────────────────────────────────────────────────────────────────────
# Semantic description (mirrors gen_manual_adoc.py logic, simplified for MkDocs)
# ─────────────────────────────────────────────────────────────────────────────

_INSN_DESCRIPTIONS: dict[str, str] = {
    "ADD": "Integer addition. Writes the sum of two registers to the destination.",
    "ADDI": "Integer add-immediate. Adds a sign-extended 12-bit immediate to a register.",
    "ADDW": "32-bit word integer addition.",
    "ADDIW": "32-bit word add-immediate.",
    "SUB": "Integer subtraction.",
    "SUBW": "32-bit word integer subtraction.",
    "AND": "Bitwise AND of two registers.",
    "ANDI": "Bitwise AND with an immediate.",
    "ANDW": "32-bit word bitwise AND.",
    "ANDIW": "32-bit word AND-immediate.",
    "OR": "Bitwise OR of two registers.",
    "ORI": "Bitwise OR with an immediate.",
    "ORW": "32-bit word bitwise OR.",
    "ORIW": "32-bit word OR-immediate.",
    "XOR": "Bitwise XOR of two registers.",
    "XORI": "Bitwise XOR with an immediate.",
    "XORW": "32-bit word bitwise XOR.",
    "XORIW": "32-bit word XOR-immediate.",
    "SLL": "Logical left shift by the value in SrcR.",
    "SLLI": "Logical left shift by an immediate amount.",
    "SLLW": "32-bit word logical left shift.",
    "SLLIW": "32-bit word logical left shift (immediate).",
    "SRL": "Logical right shift by the value in SrcR.",
    "SRLI": "Logical right shift by an immediate amount.",
    "SRLW": "32-bit word logical right shift.",
    "SRLIW": "32-bit word logical right shift (immediate).",
    "SRA": "Arithmetic right shift by the value in SrcR.",
    "SRAI": "Arithmetic right shift by an immediate amount.",
    "SRAW": "32-bit word arithmetic right shift.",
    "SRAIW": "32-bit word arithmetic right shift (immediate).",
    "MUL": "Integer multiply (lower product written to destination).",
    "MULU": "Integer multiply (unsigned).",
    "MULW": "32-bit word integer multiply.",
    "MULUW": "32-bit word integer multiply (unsigned).",
    "MADD": "Multiply-add: `Dest = SrcD + SrcL * SrcR`.",
    "MADDW": "32-bit word multiply-add.",
    "DIV": "Signed integer division.",
    "DIVU": "Unsigned integer division.",
    "DIVW": "32-bit word signed integer division.",
    "DIVUW": "32-bit word unsigned integer division.",
    "REM": "Signed integer remainder.",
    "REMU": "Unsigned integer remainder.",
    "REMW": "32-bit word signed remainder.",
    "REMUW": "32-bit word unsigned remainder.",
    "LUI": "Load upper immediate. Materializes a 20-bit constant in the upper bits of the destination.",
    "ADDTPC": "PC-relative addition. Adds an immediate to the current PC/TPC and writes the result.",
    "SETRET": "Materializes a return address (ra) using a PC-relative offset. Used in call headers.",
    "BSTART": "Block split marker. Terminates the current basic block and begins the next. Encodes block type and transition kind.",
    "BSTOP": "Block termination marker. Ends the current basic block.",
    "SETC": "Sets the block-commit condition/argument consumed by subsequent conditional block transitions.",
    "B.EQ": "Conditional branch taken when SrcL equals SrcR.",
    "B.NE": "Conditional branch taken when SrcL not equal to SrcR.",
    "B.LT": "Conditional branch taken when SrcL is less than SrcR (signed).",
    "B.GE": "Conditional branch taken when SrcL is greater than or equal to SrcR (signed).",
    "B.LTU": "Conditional branch taken when SrcL is less than SrcR (unsigned).",
    "B.GEU": "Conditional branch taken when SrcL is greater than or equal to SrcR (unsigned).",
    "J": "Unconditional PC-relative jump to a target label.",
    "JR": "Jump register: PC-relative or register-based jump to the address in a register.",
    "EBREAK": "Environment break instruction. Traps to the debugging or OS handler.",
    "FENCE": "Memory ordering fence.",
    "FENCE.I": "Instruction-cache fence. Synchronizes instruction fetch with prior stores.",
    "FENCE.D": "Data memory ordering fence.",
    "ASSERT": "Architectural assertion. Traps if the condition register is zero.",
    "ACRC": "Architectural control (ring call). Calls an implementation-defined ACR.",
    "ACRE": "Architectural control (ring entry). Enters an implementation-defined ACR.",
    "BC.IALL": "Branch-predictor cache invalidate all entries.",
    "BC.IVA": "Branch-predictor cache invalidate by address.",
    "DC.CISW": "Data cache clean-and-invalidate by set/way.",
    "DC.IVA": "Data cache invalidate by address.",
    "DC.ISW": "Data cache invalidate by set/way.",
    "IC.IALLU": "Instruction cache invalidate all (PoU).",
    "IC.IALLUIS": "Instruction cache invalidate all (PoU, surely).",
    "IC.IVAU": "Instruction cache invalidate by address.",
    "CSEL": "Conditional select. `Dest = (SrcP != 0) ? SrcL : SrcR`.",
    "BFI": "Bit-field insert. Writes selected bits from SrcL into the destination.",
    "BXS": "Bit-field extract signed.",
    "BXU": "Bit-field extract unsigned.",
    "BCNT": "Population count. Counts the number of set bits in a register.",
    "CLZ": "Count leading zeros.",
    "CTZ": "Count trailing zeros.",
    "REV": "Bit-reversal operation.",
    "BIC": "Bit clear / AND-NOT.",
    "BIS": "Bit set / OR.",
    "FABS": "Floating-point absolute value.",
    "FNEG": "Floating-point negate (flip sign bit).",
    "FADD": "Floating-point addition.",
    "FSUB": "Floating-point subtraction.",
    "FMUL": "Floating-point multiplication.",
    "FDIV": "Floating-point division.",
    "FSQRT": "Floating-point square root.",
    "FMIN": "Floating-point minimum (quiet NaN-aware).",
    "FMAX": "Floating-point maximum (quiet NaN-aware).",
    "FEQ": "Floating-point equality comparison. Writes 1 if ordered and equal.",
    "FLT": "Floating-point less-than comparison (ordered).",
    "FGE": "Floating-point greater-or-equal comparison (ordered).",
    "FCVT": "Floating-point format conversion.",
    "CMP.EQ": "Compare equal. Sets destination to 1 if operands are equal.",
    "CMP.NE": "Compare not-equal.",
    "CMP.LT": "Compare less-than (signed).",
    "CMP.GE": "Compare greater-or-equal (signed).",
    "CMP.LTU": "Compare less-than (unsigned).",
    "CMP.GEU": "Compare greater-or-equal (unsigned).",
    "MAX": "Integer max (signed).",
    "MIN": "Integer min (signed).",
    "FMAX": "Floating-point maximum.",
    "FMIN": "Floating-point minimum.",
}


def _describe_instruction(mnemonic: str, group: str, asm: str) -> str:
    """Derive a one-line description for an instruction mnemonic."""
    enc, core, parts = _mnemonic_core(mnemonic)
    root = parts[0].upper() if parts else core.upper()
    sub = parts[1].upper() if len(parts) > 1 else ""

    # Prefixes
    prefix = ""
    if enc == "C":
        prefix = "[16-bit C.] "
    elif enc == "HL":
        prefix = "[48-bit HL.] "
    elif enc == "V":
        prefix = "[64-bit V.] "

    # Check hardcoded map
    if mnemonic in _INSN_DESCRIPTIONS:
        return prefix + _INSN_DESCRIPTIONS[mnemonic]

    # Loads
    if "Load" in group or "load" in asm.lower():
        width_map = {"B": 8, "BU": 8, "H": 16, "HU": 16, "W": 32, "WU": 32, "D": 64}
        for suf, w in width_map.items():
            if core.upper().endswith(suf):
                sign = "signed " if suf in ("B", "H", "W") else ""
                return f"{prefix}Loads a {sign}{w}-bit value from memory."
        return f"{prefix}Loads a value from memory into a register."

    # Stores
    if "Store" in group or "store" in asm.lower():
        return f"{prefix}Stores a register value to memory."

    # Branches
    if group == "Branch":
        return f"{prefix}Conditional PC-relative branch."

    # Block control
    if root in ("BSTART", "BSTOP", "SETC", "B"):
        if root == "BSTART":
            if sub == "CALL":
                return (
                    f"{prefix}Atomic fused call with independent call-target and "
                    "return-target fields; transfers to the call block and writes `ra`. "
                    "This exact aggregate is distinct from the generic bare-call form, "
                    "which preserves `ra` and requires an adjacent `SETRET` or `C.SETRET`."
                )
            return f"{prefix}Terminates the current block and begins the next."
        if root == "BSTOP":
            return f"{prefix}Marks the end of the current block."
        if root == "SETC":
            return f"{prefix}Sets the block-commit condition."

    # ALU arithmetic (generic)
    arith_ops = {
        "ADD": "Integer addition.", "SUB": "Integer subtraction.",
        "AND": "Bitwise AND.", "OR": "Bitwise OR.", "XOR": "Bitwise XOR.",
        "SLL": "Logical left shift.", "SRL": "Logical right shift.",
        "SRA": "Arithmetic right shift.",
        "MUL": "Integer multiply.", "DIV": "Signed integer division.",
        "DIVU": "Unsigned integer division.",
        "REM": "Signed integer remainder.", "REMU": "Unsigned integer remainder.",
        "NEG": "Integer negate.", "NOT": "Bitwise NOT.",
        "CLZ": "Count leading zeros.", "CTZ": "Count trailing zeros.",
        "BCNT": "Population count.",
        "REV": "Bit-reversal.",
        "BXS": "Bit-field extract signed.", "BXU": "Bit-field extract unsigned.",
        "BFI": "Bit-field insert.", "BIC": "Bit clear.", "BIS": "Bit set.",
        "CSEL": "Conditional select.",
    }
    if root in arith_ops:
        return f"{prefix}{arith_ops[root]}"

    # Atomics
    if "Atomic" in group:
        return f"{prefix}Atomic memory read-modify-write operation."

    # System / control
    if group == "Execution Control":
        return f"{prefix}Execution control instruction."

    # Cache / TLB maintenance
    if "Cache" in group or "Cache" in root:
        return f"{prefix}Cache maintenance operation."

    return f"{prefix}Instruction from the {group} group."


def _catalog_description(inst: dict) -> str:
    """Use a specific description, falling back to the catalog summary."""
    derived = _describe_instruction(
        str(inst["mnemonic"]),
        str(inst.get("group", "Ungrouped")),
        str(inst.get("asm", "")),
    )
    if "Instruction from the " not in derived:
        return derived
    note = _collapse_ws(str(inst.get("note") or ""))
    if note:
        return note
    return derived


# ─────────────────────────────────────────────────────────────────────────────
# Page templates
# ─────────────────────────────────────────────────────────────────────────────


def _build_index_page(
    groups: OrderedDict[str, list[dict]],
    instructions: list[dict],
    out_path: str,
    spec_version: str,
) -> None:
    """Build the ISA index page with hero, chapter grid, group grid, and mnemonics."""
    n_groups = len(groups)
    n_instr = len(instructions)

    # ── Hero section ──────────────────────────────────────────────────────────
    hero = """<!-- Hero Banner -->
<div class="isa-hero">

**ISA Version:** __SPEC_VERSION__ &nbsp;·&nbsp; **__FORM_COUNT__ instruction forms** &nbsp;·&nbsp; **__GROUP_COUNT__ groups** &nbsp;·&nbsp; **4 encoding formats**

---

Browse by chapter, instruction group, or search by mnemonic. Each instruction page includes its encoding diagram, assembly syntax, and description.

**Jump to:** [Encoding Formats](encoding.md) · [Groups Index](groups/index.md) · [A–Z Index](instructions/index.md)

</div>

---

## Browse by Chapter

The LinxISA manual is organized into 12 chapters covering distinct functional units. Click any chapter to jump to its first instruction group.

<div class="chapter-grid">

[![](assets/ch03.svg){: style="width:120px;height:80px"} **Ch 03 — Encoding Formats**{.chapter-card style="--ch03-color:#64748b"}
: Bit numbering, instruction lengths, decode tags, field colour key

[![](assets/ch04.svg){: style="width:120px;height:80px"} **Ch 04 — Block ISA**{.chapter-card style="--ch04-color:#8b5cf6"}
: BSTART, BSTOP, B.DATR, B.DIM, B.IOT, tile/SIMT control flow

[![](assets/ch11.svg){: style="width:120px;height:80px"} **Ch 11 — AGU**{.chapter-card style="--ch11-color:#059669"}
: Loads, stores, prefetch, all addressing modes

[![](assets/ch12.svg){: style="width:120px;height:80px"} **Ch 12 — ALU**{.chapter-card style="--ch12-color:#0891b2"}
: ADD, SUB, MUL, DIV, shifts, bit manip, LUI, CSEL

[![](assets/ch13.svg){: style="width:120px;height:80px"} **Ch 13 — FSU**{.chapter-card style="--ch13-color:#0ea5e9"}
: Floating-point arithmetic, FMA, format conversion

[![](assets/ch14.svg){: style="width:120px;height:80px"} **Ch 14 — AMO**{.chapter-card style="--ch14-color:#e11d48"}
: LR/SC, atomic fetch-op, CAS

[![](assets/ch15.svg){: style="width:120px;height:80px"} **Ch 15 — BBD**{.chapter-card style="--ch15-color:#8b5cf6"}
: C.BSTART, C.BSTOP, block delimiters

[![](assets/ch16.svg){: style="width:120px;height:80px"} **Ch 16 — BRU**{.chapter-card style="--ch16-color:#7c3aed"}
: Branches, CMP, SETC, SETRET, ADDTPC

[![](assets/ch17.svg){: style="width:120px;height:80px"} **Ch 17 — CMD**{.chapter-card style="--ch17-color:#6366f1"}
: B.CATR, B.DATR, B.HINT, block attributes

[![](assets/ch18.svg){: style="width:120px;height:80px"} **Ch 18 — RSV**{.chapter-card style="--ch18-color:#a16207"}
: HL.BFI, HL.MIADD, HL.MISUB

[![](assets/ch19.svg){: style="width:120px;height:80px"} **Ch 19 — SYS**{.chapter-card style="--ch19-color:#dc2626"}
: FENCE, barriers, EBREAK, ACR*, cache/TLB maintenance

[![](assets/ch20.svg){: style="width:120px;height:80px"} **Ch 20 — VEC**{.chapter-card style="--ch20-color:#2563eb"}
: V.* vector forms, shuffles, reductions, division

</div>

---

## Browse by Group

<div class="group-card-grid">
"""
    hero = (
        hero.replace("__SPEC_VERSION__", f"v{spec_version}")
        .replace("__FORM_COUNT__", str(n_instr))
        .replace("__GROUP_COUNT__", str(n_groups))
    )

    # ── Group card grid ─────────────────────────────────────────────────────
    all_items = sorted(groups.items(), key=lambda x: x[0])
    grid_items_html = []
    for group, insts in all_items:
        slug = _slug(group)
        cnt = len(insts)
        grid_items_html.append(
            f"[{group} ({cnt})](groups/{slug}.md){{.group-card}}"
        )

    # 4 per row — join into groups of 4
    grid_chunks = [grid_items_html[i:i+4] for i in range(0, len(grid_items_html), 4)]
    grid_lines = [" ".join(chunk) for chunk in grid_chunks]
    group_grid = hero + "\n".join(grid_lines) + """

</div>

See also: [Groups Index (detailed)](groups/index.md) · [All Instructions A–Z](instructions/index.md)

---

## Instruction Quick Index

Use **Ctrl+F** / **Cmd+F** to search, or browse the [full alphabetical list](instructions/index.md).

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
"""

    # ── Mnemonic table ───────────────────────────────────────────────────────
    mnem_rows = []
    for group, insts in groups.items():
        seen: set[str] = set()
        for inst in insts:
            m = inst["mnemonic"]
            if m in seen:
                continue
            seen.add(m)
            desc = _catalog_description(inst)
            gslug = _slug(group)
            bits = inst.get("length_bits", "?")
            mnem_rows.append(
                f"| [{m}](instructions/{_slug(m)}.md) | {gslug} | {bits} | {_collapse_ws(desc)} |"
            )
            if len(seen) >= 5:
                break

    # Build full content
    content_parts = [
        "# LinxISA Instruction Reference",
        "",
        group_grid,
        "\n".join(mnem_rows),
        "",
        f"[View all {n_instr} instruction forms →](instructions/index.md)",
    ]

    full_content = "\n".join(content_parts)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_content + "\n")


def _render_index_page(
    groups: OrderedDict[str, list[dict]],
    instructions: list[dict],
    out_path: str,
    spec_version: str,
) -> None:
    _build_index_page(groups, instructions, out_path, spec_version)


_ENCODING_PAGE = """# Instruction Encoding Formats

> **ISA Version:** v{spec_version} &nbsp;|&nbsp; **Chapter 03** of the ISA Manual

LinxISA v{spec_version} supports four instruction lengths in a little-endian
halfword-oriented model. Bit positions are shown as `[msb:0]`
(MSB leftmost, LSB rightmost), matching ARM and RISC-V conventions.

## Instruction Lengths

| Namespace | Format | Bits | Composition | Example |
|-----------|--------|------|-------------|---------|
| **C.** | C16 | 16 | Single 16-bit part | `C.ADD`, `C.LD`, `C.BSTART.FP` |
| *(base)* | LX32 | 32 | Single 32-bit part | `ADD`, `LD`, `BSTART CALL` |
| **HL.** | HL48 | 48 | 16-bit prefix + 32-bit main | `HL.LDI`, `HL.CASB`, `HL.SETRET` |
| **V.** | V64 | 64 | 32-bit prefix + 32-bit main | `V.ADD`, `V.FMADD`, `V.DIV` |

> **Note:** 48-bit (`HL.*`) and 64-bit (`V.*`) forms are *prefix + main* compositions.
> The prefix augments the following instruction and has no standalone semantics.

## Decode Format Tags

Each instruction carries a decode `Type` tag describing its operand field layout:

### 16-bit (C.) Decode Types

| Tag | Typical operands |
|-----|-----------------|
| `C.Type A` | `SrcL`, `SrcR` — two-register |
| `C.Type B` | `SrcL`, `uimm5` — register + small immediate |
| `C.Type C` | `SrcL`, `Func` — register + function code |
| `C.Type D` | `SrcL`, `RegDst` — register move |
| `C.Type E` | `RegDst`, `uimm5` — move-immediate / setret |
| `C.Type F` | `Func`, `uimm5` — function + small immediate |
| `C.Type G` | immediate-only (block markers) |
| `C.Type H` | `imm10` — larger immediate |
| `C.Type I` | `imm12` — PC-relative forms |

### 32-bit Decode Types

| Tag | Typical operands |
|-----|-----------------|
| `Type A` | `RegDst`, `SrcL`, `SrcR` [, `SrcD`] — 3-source |
| `Type B` | `RegDst`, `SrcL`, `SrcR` + small `imm` |
| `Type C` | `SrcL`, `SrcR` + 2 immediates |
| `Type D` | `RegDst`, `SrcL` + `simm` — compare/branch |
| `Type F` | `RegDst`, `SrcL` + `simm` — load/store |
| `Type G` | `RegDst` + `simm` — load-immediate |
| `Type H` | `SrcL`, `SrcR` + `simm` — ALU-immediate |

## Encoding Space

| Encoding | Major opcode bits | Slots | Usage |
|----------|-----------------|-------|-------|
| C16 | `[15:13]` | 8 | Compressed 16-bit forms |
| LX32 | `[31:26]` | 64 | Base 32-bit forms |
| HL48 | `[47:40]` | 256 | High-level prefix |
| V64 | `[63:58]` | 64 | Vector prefix |

See [Encoding Space Analysis](../reference/encoding_space_report.md) for the full
conflict-free allocation table.

The [PTO ISA encoding workbook](encoding/PTO-ISA-Encoding.xlsx) is provided
only as a non-normative review aid. It is not a generator input and cannot
override the checked-in v0.58 JSON/opcode sources.

## Field Colour Key

![Encoding legend](wavedrom/encoding_legend.svg)

| Colour | Field | Colour | Field |
|--------|-------|--------|-------|
| Green | Rd / RegDst | Purple | funct / opcode |
| Cyan | Rs1 / SrcL | Pink | shamt |
| Teal | Rs2 / SrcR | Amber | imm / offset |
| Orange | Rs3 / SrcD | Gray | reserved / zero |

## Example Diagrams

### 32-bit: ADD

![ADD encoding](wavedrom/enc_add.svg)

### 16-bit: C.ADD

![C.ADD encoding](wavedrom/enc_c_add.svg)

### 48-bit: HL.LDI

![HL.LDI encoding](wavedrom/enc_hl_ldi.svg)

### 64-bit: V.ADD

![V.ADD encoding](wavedrom/enc_v_add_parts.svg)

## See Also

- [Full ISA Manual overview](https://github.com/LinxISA/linx-isa/tree/main/docs/architecture/isa-manual/src)
- [Instruction reference index](index.md)
- [Encoding Space Analysis](../reference/encoding_space_report.md)
"""

def _render_encoding_page(out_path: str, spec_version: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(_ENCODING_PAGE.format(spec_version=spec_version))


def _render_group_index(
    groups: OrderedDict, out_path: str, spec_version: str
) -> None:
    """Build docs/isa/groups/index.md."""
    rows = []
    for group, insts in groups.items():
        slug = _slug(group)
        count = len(insts)
        ch_info = get_manual_chapter(group)
        if ch_info:
            ch_num, ch_title = ch_info
            ch_cell = f"**Ch {ch_num}** — [source](index.md)"
        else:
            ch_cell = "—"
        mnems = sorted(set(i["mnemonic"] for i in insts))
        # Show up to 8 mnemonics
        samples = ", ".join(f"`{m}`" for m in mnems[:8])
        if len(mnems) > 8:
            samples += f" +{len(mnems) - 8}"
        rows.append(f"| [{group}]({slug}.md) | {count} | {ch_cell} | {samples} |")

    header = f"""# Instruction Groups

Alphabetical list of all {len(groups)} instruction groups in the LinxISA v{spec_version} catalog.
See the [chapter index](index.md) for the manual organization.

| Group | Forms | Chapter | Sample mnemonics |
|-------|-------|---------|------------------|
"""
    content = header + "\n".join(rows) + "\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)


# ─────────────────────────────────────────────────────────────────────────────
# Per-group page
# ─────────────────────────────────────────────────────────────────────────────

_GROUP_PAGE_TEMPLATE = """# {group}

<div class="insn-header">

<span class="ch-tag ch-tag-{chapter_num:02d}">Ch {chapter_num:02d}</span>
&nbsp; <strong>{chapter_title}</strong> &nbsp;|&nbsp;
**Group:** {group} &nbsp;|&nbsp;
**Forms:** {form_count} &nbsp;|&nbsp;
**Unique mnemonics:** {mnem_count}

</div>

{intro}

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
{instruction_table}

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter {chapter_num}: {chapter_title}](../{chapter_link})
- [Encoding formats](../encoding.md)
"""


def _render_group_page(
    group: str,
    insts: list[dict],
    out_path: str,
    spec_version: str,
) -> None:
    mnems = sorted(set(i["mnemonic"] for i in insts))
    form_count = len(insts)
    mnem_count = len(mnems)

    # Intro paragraph
    intro = _get_group_intro(group, spec_version)

    # Instruction table
    rows = []
    seen_mnem: set[str] = set()
    for inst in insts:
        m = inst["mnemonic"]
        if m in seen_mnem:
            continue
        seen_mnem.add(m)
        asm = inst.get("asm", "—")
        length = inst.get("length_bits", "?")
        decode = inst.get("parts", [{}])[0].get("decode", "—")
        if decode is None:
            decode = "—"
        desc = _catalog_description(inst)
        rows.append(f"| [{m}](../instructions/{_slug(m)}.md) | `{asm}` | {length} | {decode} | {desc} |")

    ch_info = get_manual_chapter(group)
    if ch_info:
        ch_num, ch_title = ch_info
    else:
        ch_num, ch_title = 0, "ISA Manual"

    content = _GROUP_PAGE_TEMPLATE.format(
        group=group,
        form_count=form_count,
        mnem_count=mnem_count,
        intro=intro,
        instruction_table="\n".join(rows),
        chapter_num=ch_num,
        chapter_title=ch_title,
        chapter_link="index.md",
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)


def _get_group_intro(group: str, spec_version: str) -> str:
    intros = {
        "Arithmetic": "Integer arithmetic instructions operating on general-purpose registers.",
        "Arithmetic Operation": "Extended integer arithmetic, including 64-bit forms and vector variants.",
        "Arithmetic Operation 32bit": "32-bit (word) integer arithmetic instructions.",
        "Arithmetic Operation 64bit": "Full 64-bit integer arithmetic instructions.",
        "Atomic": "Atomic memory operations including load-reserved, store-conditional, and fetch-op variants.",
        "Atomic Operation": "Atomic read-modify-write operations on memory.",
        "BSTART": "Block split instructions that end one basic block and begin the next.",
        "BSTART": "Block split instructions with CALL/RET/commit argument encoding.",
        "Block Argument": "Instructions that declare block argument bindings (input registers).",
        "Block Control Attribute": "Block attribute-setting instructions.",
        "Block Data Attribute": "Block data annotation instructions.",
        "Block Dimension": "Instructions that set block loop-dimension registers.",
        "Block Hint": "Block execution hint instructions for the front-end.",
        "Block Input & Output": "Block I/O declaration instructions.",
        "Block Offset": "Block text/offset annotation instructions.",
        "Block Split": "Block structural instructions (BSTART, BSTOP, FENTRY, etc.).",
        "Branch": "Conditional PC-relative branch instructions.",
        "C.BSTART": "16-bit compressed block split instructions.",
        "C.TINST": "16-bit compressed miscellaneous instructions.",
        "C.UNARY": "16-bit compressed unary operations.",
        "Cache Maintain": "Cache maintenance operations (I-cache, D-cache, branch predictor).",
        "Compare Instruction": "Integer comparison instructions that write a boolean result.",
        "Compound Operation": "Compound operations (e.g., conditional select).",
        "Concat": "Concatenation / combine operations.",
        "Division": "Signed and unsigned integer division.",
        "Execution Control": "Architectural control, EBREAK, ASSERT, ACR operations.",
        "Floating-point Arithmetic": "Scalar floating-point arithmetic instructions.",
        "Floating-point Arithmetic": "Full-precision floating-point operations.",
        "Floating-point Compare": "Floating-point comparison instructions.",
        "Format Convert": "Floating-point and integer format conversion instructions.",
        "General": "General high-level operations.",
        "General Manager": "Queue and general management operations.",
        "Immediate": "Immediate materialization instructions (LUI, ADDTPC, HL.LUI).",
        "Load Immediate Offset": "Load instructions with immediate offsets.",
        "Load Long Offset": "48-bit load instructions with extended offsets.",
        "Load PC-Relative": "PC-relative load instructions.",
        "Load Pair": "Paired-load instructions that read two consecutive values.",
        "Load Post-Index": "Load with post-index writeback.",
        "Load Pre-Index": "Load with pre-index writeback.",
        "Load Register Offset": "Load instructions with register offsets.",
        "Load Symbol": "PC-relative symbol loads.",
        "Load UnScaled": "Load instructions with unscaled immediate offsets.",
        "Long Immediate": "Long immediate materialization (HL.LIS, HL.LIU).",
        "Max-Min": "Integer max/min instructions.",
        "Move": "Register/memory move instructions.",
        "Multi-Cycle ALU": "Multi-cycle ALU operations: division, remainder, and extended multiply.",
        "PC-Relative": "PC-relative address computation instructions.",
        "Prefetch": "Memory prefetch hint instructions.",
        "RESERVE": "Reservation and conditional-update operations.",
        "Reduce Operation with Register": "Vector reduction operations.",
        "Set Commit Argument": "SETC instructions that encode the block-commit condition.",
        "Shuffle": "Vector lane shuffle operations.",
        "SSR Access": "System register (SSR/LSR) access instructions.",
        "Store Immediate Offset": "Store instructions with immediate offsets.",
        "Store Long Offset": "48-bit store instructions with extended offsets.",
        "Store Offset": "Store instructions with register offsets.",
        "Store PC-Relative": "PC-relative store instructions.",
        "Store Pair": "Paired-store instructions.",
        "Store Post-Index": "Store with post-index writeback.",
        "Store Pre-Index": "Store with pre-index writeback.",
        "Store Register Offset": "Store instructions with register offsets.",
        "Store Symbol": "PC-relative symbol stores.",
        "Three Source Integer": "Three-source integer operations.",
        "Three-Source Floating Point": "Three-source floating-point operations.",
        "Two-Source Floating Point": "Two-source floating-point operations.",
        "Bit Manipulation": "Bit manipulation operations (vector forms).",
        "Bit Operation": "Bit manipulation operations (scalar forms).",
    }
    return intros.get(
        group,
        f"Instructions in the **{group}** group of the LinxISA v{spec_version} catalog.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Per-instruction page
# ─────────────────────────────────────────────────────────────────────────────

_INSN_PAGE_TEMPLATE = """# {mnemonic}

<div class="insn-header">

{mnemonic_badge} **Group:** <a href="../groups/{group_slug}.md">{group}</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-{chapter_num:02d}">Ch {chapter_num:02d}</span>
&nbsp; <strong>{chapter_title}</strong> &nbsp;|&nbsp;
**Length:** <code>{length}</code> &nbsp;|&nbsp; **Decode:** <code>{decode_tag}</code>

</div>

## Assembly Syntax

{assembly_forms}
{assembly_aliases}
## Encoding

<div class="enc-diagram">

{wavedrom_svg}

</div>

## Description

{description}

## Pseudocode (informative)

```c
{pseudocode}
```

## Encoding Notes

{encoding_notes}

## Full Catalog Forms

{forms_table_header}
{all_forms_table}

<div class="insn-nav">

← [{group}](../groups/{group_slug}.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
"""


def _render_instruction_page(
    inst: dict,
    all_forms: list[dict],
    svg_dir: str,
    out_path: str,
) -> None:
    mnemonic = inst["mnemonic"]
    group = inst.get("group", "Ungrouped")
    group_slug = _slug(group)
    length = inst.get("length_bits", "?")
    decode_tag = inst.get("parts", [{}])[0].get("decode", "—") or "—"
    asm = inst.get("asm", "")
    desc = _catalog_description(inst)

    # Assembly forms (unique by asm string)
    seen_asm: set[str] = set()
    asm_list: list[str] = []
    for f in all_forms:
        a = f.get("asm", "")
        if a and a not in seen_asm:
            seen_asm.add(a)
            asm_list.append(a)
    asm_block = "\n".join(f"- `{a}`" for a in asm_list) if asm_list else "_No assembly forms defined._"

    alias_block = ""
    aliases = inst.get("accepted_assembly_mnemonics")
    canonical_by_engine = inst.get("canonical_assembly_by_engine")
    carrier = inst.get("carrier_mnemonic")
    if isinstance(aliases, list) and isinstance(canonical_by_engine, dict) and carrier == mnemonic:
        alias_lines = [
            "## Canonical Semantic Aliases",
            "",
            "- `BSTART.VEC TileOp, DataType` is accepted only when `TileOp` is catalogued for VEC.",
            "- `BSTART.SFU TileOp, DataType` is accepted only when `TileOp` is catalogued for SFU.",
            "- `BSTART.TEPL Mode, Function, DataType` remains the raw compatibility spelling.",
            "- Canonical disassembly emits the VEC or SFU alias selected by the Tile operation catalog.",
            "",
        ]
        alias_block = "\n" + "\n".join(alias_lines)

    # One stable asset per form. Duplicate mnemonics must not overwrite one
    # another, so their filenames are based on the catalog form ID.
    figures: list[str] = []
    for form in all_forms:
        svg_file = _encoding_asset_filename(form, len(all_forms))
        svg_abs = os.path.join(svg_dir, svg_file) if svg_dir else ""
        if not svg_dir or not os.path.isfile(svg_abs):
            raise FileNotFoundError(
                f"missing generated encoding asset {svg_abs or svg_file}; run gen_encoding_svg.py"
            )
        if len(all_forms) == 1:
            figures.append(
                f'<figure>\n<img src="../wavedrom/{svg_file}" alt="{mnemonic} encoding" width="100%" />\n'
                "<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>\n</figure>"
            )
        else:
            form_id = str(form["id"])
            form_asm = _collapse_ws(str(form.get("asm") or mnemonic))
            figures.append(
                f'<figure id="encoding-{form_id}">\n'
                f'<img src="../wavedrom/{svg_file}" alt="{mnemonic} encoding form {form_id}" width="100%" />\n'
                f'<figcaption><code>{form_id}</code> — <code>{form_asm}</code>. '
                "MSB is on the left, LSB is on the right.</figcaption>\n</figure>"
            )
    wavedrom_svg = "\n\n".join(figures)

    # Pseudocode
    pseudo = _derive_pseudocode(mnemonic, group, asm)
    pseudo_block = pseudo if pseudo else "// No pseudocode available for this instruction."

    # Encoding notes
    notes_list = []
    for f in all_forms:
        note = f.get("note", "")
        if note and note not in notes_list:
            notes_list.append(note)
    if notes_list:
        notes_block = "\n".join(f"- `{_collapse_ws(n)}`" for n in notes_list)
    else:
        notes_block = "_No additional encoding notes._"

    # All catalog forms table
    form_rows = []
    for f in all_forms:
        fa = f.get("asm", "—")
        fl = f.get("length_bits", "?")
        fd = f.get("parts", [{}])[0].get("decode", "—") or "—"
        if len(all_forms) == 1:
            form_rows.append(f"| `{fa}` | {fl} | {fd} |")
        else:
            form_id = str(f["id"])
            svg_file = _encoding_asset_filename(f, len(all_forms))
            form_rows.append(
                f"| `{form_id}` | `{fa}` | {fl} | {fd} | [SVG](../wavedrom/{svg_file}) |"
            )
    if len(all_forms) == 1:
        forms_table_header = "| Assembly | Length | Decode |\n|----------|--------|--------|"
        all_forms_table = "\n".join(form_rows) if form_rows else "| — | — | — |"
    else:
        forms_table_header = (
            "| Form ID | Assembly | Length | Decode | Encoding |\n"
            "|---------|----------|--------|--------|----------|"
        )
        all_forms_table = "\n".join(form_rows) if form_rows else "| — | — | — | — | — |"

    # Mnemonic badge (C./HL./V.) — uses CSS classes for professional styling
    if mnemonic.startswith("C."):
        badge = '<span class="badge-16">16-bit C.</span>'
    elif mnemonic.startswith("HL."):
        badge = '<span class="badge-48">48-bit HL.</span>'
    elif mnemonic.startswith("V."):
        badge = '<span class="badge-64">64-bit V.</span>'
    else:
        badge = '<span class="badge-32">32-bit Base</span>'

    ch_info = get_manual_chapter(group)
    if ch_info:
        ch_num, ch_title = ch_info
    else:
        ch_num, ch_title = 0, "ISA Manual"

    content = _INSN_PAGE_TEMPLATE.format(
        mnemonic=mnemonic,
        mnemonic_badge=badge,
        group=group,
        group_slug=group_slug,
        length=length,
        decode_tag=decode_tag,
        form_count=len(all_forms),
        assembly_forms=asm_block,
        assembly_aliases=alias_block,
        wavedrom_svg=wavedrom_svg,
        description=desc,
        pseudocode=pseudo_block,
        encoding_notes=notes_block,
        forms_table_header=forms_table_header,
        all_forms_table=all_forms_table,
        chapter_num=ch_num,
        chapter_title=ch_title,
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)


def _derive_pseudocode(mnemonic: str, group: str, asm: str) -> str:
    """Derive a compact pseudocode string from mnemonic conventions."""
    enc, core, parts = _mnemonic_core(mnemonic)
    root = parts[0].upper() if parts else core.upper()
    sub = parts[1].upper() if len(parts) > 1 else ""

    if root == "BSTART":
        if sub == "CALL":
            call_imm = "simm25" if enc == "HL" else "simm12"
            setret_base = 4 if enc == "HL" else 2
            return (
                "P = CurrentPC();\n"
                f"call_target = P + (SignExtend({call_imm}) << 1);\n"
                f"ra = (P + {setret_base}) + (ZeroExtend(uimm5) << 1);\n"
                "AtomicCallTransfer(call_target, ra);"
            )
        return "EndBlock(); BeginNextBlock(/* kind */);"
    if root == "BSTOP":
        return "EndBlock();"
    if root == "SETC":
        return "SetCommitArgument(/* condition */);"
    if root == "LUI":
        return "rd = ZeroExtend(imm20) << 12;"
    if root == "ADDTPC":
        return "rd = PC + SignExtend(imm);"
    if root == "SETRET":
        return "ra = PC + ZeroExtend(imm << 1);"
    if root in {"EBREAK", "ASSERT"}:
        return "Trap(EBREAK);"
    if root == "FENCE":
        return "Fence(/* ordering */);"
    if "Load" in group:
        return "rd = Load(/* addr */);"
    if "Store" in group:
        return "Store(/* addr */, rs2);"
    if root == "ADD":
        return "rd = rs1 + rs2;"
    if root == "ADDI":
        return "rd = rs1 + SignExtend(imm12);"
    if root == "SUB":
        return "rd = rs1 - rs2;"
    if root == "AND":
        return "rd = rs1 & rs2;"
    if root == "ANDI":
        return "rd = rs1 & SignExtend(imm12);"
    if root == "OR":
        return "rd = rs1 | rs2;"
    if root == "ORI":
        return "rd = rs1 | SignExtend(imm12);"
    if root == "XOR":
        return "rd = rs1 ^ rs2;"
    if root == "XORI":
        return "rd = rs1 ^ SignExtend(imm12);"
    if root == "SLL":
        return "rd = rs1 << (rs2 & 63);"
    if root == "SLLI":
        return "rd = rs1 << shamt;"
    if root == "SRL":
        return "rd = rs1 >> rs2 (logical);"
    if root == "SRLI":
        return "rd = rs1 >> shamt (logical);"
    if root == "SRA":
        return "rd = rs1 >> rs2 (arith);"
    if root == "SRAI":
        return "rd = rs1 >> shamt (arith);"
    if root == "MUL":
        return "rd = Trunc64(rs1 * rs2);"
    if root == "DIV":
        return "rd = (rs2 != 0) ? (rs1 / rs2) : 0;"
    if root == "DIVU":
        return "rd = (rs2 != 0) ? UnsignedDiv(rs1, rs2) : 0;"
    if root == "REM":
        return "rd = (rs2 != 0) ? (rs1 % rs2) : rs1;"
    if root == "CSEL":
        return "rd = (rs_p != 0) ? rs1 : rs2;"
    if root == "BCNT":
        return "rd = PopCount(rs1);"
    if root == "CLZ":
        return "rd = CountLeadingZeros(rs1);"
    if root == "CTZ":
        return "rd = CountTrailingZeros(rs1);"
    if root == "B.EQ":
        return "if (rs1 == rs2) TPC = target;"
    if root == "B.NE":
        return "if (rs1 != rs2) TPC = target;"
    if root == "B.LT":
        return "if (signed(rs1) < signed(rs2)) TPC = target;"
    if root == "B.GE":
        return "if (signed(rs1) >= signed(rs2)) TPC = target;"
    if root in {"FEQ", "FEQS"}:
        return "rd = (fs1 == fs2) ? 1 : 0;"
    if root == "FMAX":
        return "rd = fmax(fs1, fs2);"
    if root == "FMIN":
        return "rd = fmin(fs1, fs2);"
    if root == "FABS":
        return "rd = fabs(fs1);"
    if root == "CMP.EQ":
        return "rd = (rs1 == rs2) ? 1 : 0;"

    # Generic fallback
    return f"// Execute {mnemonic} as defined by the {group} semantics."


# ─────────────────────────────────────────────────────────────────────────────
# Master instruction index page
# ─────────────────────────────────────────────────────────────────────────────

def _render_instruction_index(
    instructions: list[dict],
    groups: OrderedDict,
    out_path: str,
    spec_version: str,
) -> None:
    """Build the searchable alphabetical index of all canonical instruction forms."""

    # Build alphabetical index by first letter
    by_letter: dict[str, list[dict]] = {}
    for inst in instructions:
        m = inst["mnemonic"]
        letter = m[0].upper()
        by_letter.setdefault(letter, []).append(inst)

    sections = []
    for letter in sorted(by_letter.keys()):
        insts = sorted(by_letter[letter], key=lambda x: x["mnemonic"].lower())
        rows = []
        for inst in insts:
            m = inst["mnemonic"]
            g = inst.get("group", "Ungrouped")
            gslug = _slug(g)
            l = inst.get("length_bits", "?")
            desc = _catalog_description(inst)
            rows.append(f"| [{m}]({_slug(m)}.md) | [{g}](../groups/{gslug}.md) | {l} | {desc} |")
        sections.append(f"### {letter}\n\n| Mnemonic | Group | Bits | Description |\n|----------|-------|------|-------------|\n" + "\n".join(rows))

    header = f"""# All Instructions

Complete alphabetical index of all **{len(instructions)}** instruction forms in the LinxISA v{spec_version} catalog.

Use **Ctrl+F** / **Cmd+F** to search, or click a letter below to jump to it.

"""
    letter_nav = " | ".join(
        f"[{letter}](#{letter.lower()})" for letter in sorted(by_letter.keys())
    )
    content = header + letter_nav + "\n\n" + "\n\n".join(sections) + "\n"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", default="isa/v0.58/linxisa-v0.58.json")
    ap.add_argument("--out-dir", default="docs/isa")
    ap.add_argument("--svg-dir", default="docs/isa/wavedrom")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--check", action="store_true", help="Check if pages are up-to-date")
    args = ap.parse_args()

    spec = _read_json(args.spec)
    spec_version = str(spec.get("version", "?"))
    instructions: list[dict] = list(spec.get("instructions", []))

    requested_out_dir = os.path.abspath(args.out_dir)
    temp_root: tempfile.TemporaryDirectory[str] | None = None
    if args.check:
        temp_root = tempfile.TemporaryDirectory(prefix="linxisa-doc-check-")
        out_dir = os.path.join(temp_root.name, "isa")
    else:
        out_dir = requested_out_dir
    svg_dir = args.svg_dir

    # Ensure subdirectories exist
    for sub in ("groups", "instructions", "wavedrom"):
        os.makedirs(os.path.join(out_dir, sub), exist_ok=True)

    groups = _group_instructions(instructions)

    if args.verbose:
        print(f"[gen_isa_pages] ISA v{spec_version} — {len(instructions)} forms, {len(groups)} groups")

    # ── Index page ────────────────────────────────────────────────────────────
    _render_index_page(
        groups, instructions, os.path.join(out_dir, "index.md"), spec_version
    )
    if args.verbose:
        print(f"  wrote index.md")

    # ── Encoding page ─────────────────────────────────────────────────────────
    _render_encoding_page(os.path.join(out_dir, "encoding.md"), spec_version)
    if args.verbose:
        print(f"  wrote encoding.md")

    # ── Group index ────────────────────────────────────────────────────────────
    _render_group_index(
        groups, os.path.join(out_dir, "groups", "index.md"), spec_version
    )
    if args.verbose:
        print(f"  wrote groups/index.md")

    # ── Per-group pages ───────────────────────────────────────────────────────
    for group, insts in groups.items():
        slug = _slug(group)
        out_path = os.path.join(out_dir, "groups", f"{slug}.md")
        _render_group_page(group, insts, out_path, spec_version)
        if args.verbose:
            print(f"  wrote groups/{slug}.md")

    # ── Master instruction index ───────────────────────────────────────────────
    _render_instruction_index(
        instructions,
        groups,
        os.path.join(out_dir, "instructions", "index.md"),
        spec_version,
    )
    if args.verbose:
        print(f"  wrote instructions/index.md")

    # ── Per-instruction pages ──────────────────────────────────────────────────
    # Group by mnemonic (one page per unique mnemonic, all forms listed)
    mnem_map: dict[str, list[dict]] = OrderedDict()
    for inst in instructions:
        m = inst["mnemonic"]
        mnem_map.setdefault(m, []).append(inst)

    for mnemonic, forms in mnem_map.items():
        slug = _slug(mnemonic)
        out_path = os.path.join(out_dir, "instructions", f"{slug}.md")
        _render_instruction_page(forms[0], forms, svg_dir, out_path)
        if args.verbose:
            print(f"  wrote instructions/{slug}.md")

    if args.check:
        generated_files = {
            os.path.relpath(os.path.join(root, name), out_dir)
            for root, _, names in os.walk(out_dir)
            for name in names
        }
        managed_existing = {"index.md", "encoding.md"}
        for sub in ("groups", "instructions"):
            existing_dir = os.path.join(requested_out_dir, sub)
            if os.path.isdir(existing_dir):
                managed_existing.update(
                    os.path.join(sub, name)
                    for name in os.listdir(existing_dir)
                    if name.endswith(".md")
                )

        missing = sorted(generated_files - managed_existing)
        unexpected = sorted(managed_existing - generated_files)
        drift = sorted(
            rel
            for rel in generated_files & managed_existing
            if not filecmp.cmp(
                os.path.join(out_dir, rel),
                os.path.join(requested_out_dir, rel),
                shallow=False,
            )
        )
        temp_root.cleanup()
        if missing or unexpected or drift:
            for rel in missing:
                print(f"error: missing generated page: {rel}", file=sys.stderr)
            for rel in unexpected:
                print(f"error: unexpected generated page: {rel}", file=sys.stderr)
            for rel in drift:
                print(f"error: generated page drift: {rel}", file=sys.stderr)
            return 1
        print(
            f"ok: {len(mnem_map)} instruction pages and {len(groups)} group pages are current"
        )
        return 0

    expected_managed = {
        "index.md",
        "encoding.md",
        "groups/index.md",
        "instructions/index.md",
        *(f"groups/{_slug(group)}.md" for group in groups),
        *(f"instructions/{_slug(mnemonic)}.md" for mnemonic in mnem_map),
    }
    for sub in ("groups", "instructions"):
        managed_dir = os.path.join(out_dir, sub)
        for name in os.listdir(managed_dir):
            rel = os.path.join(sub, name)
            if name.endswith(".md") and rel not in expected_managed:
                os.unlink(os.path.join(out_dir, rel))

    print(f"\n[gen_isa_pages] Done — {len(mnem_map)} instruction pages, {len(groups)} group pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
