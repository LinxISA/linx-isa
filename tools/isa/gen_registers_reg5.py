#!/usr/bin/env python3
"""
Generate the complete register reference table for the LinxISA manual.

Sources:
  ~/Documents/linxisa.csv (GB2312) — register names, aliases, Chinese descriptions
  isa/v0.56/linxisa-v0.56.json — canonical code numbers

The golden CSV is a sparse matrix with 18 columns spanning 5 logical register sections:

  col[0-2]  GPR:         name | alias | description
  col[5-8]  Tile Regs:   T# name | T# desc | M# name | M# desc
                          (ACC and S also appear in this section)
  col[11-13] Scalar blk:  name | alias | description
  col[15-17] Data blk:     name | alias | description
  col[18-20] (used by data blk rows: IO + Loop + Mask entries)

For RI, RO, LB, LC, P: their names appear in col[15] and descriptions in col[17].
"""
from __future__ import annotations

import argparse
import csv as _csv
import os
import re
from typing import Dict, List, Tuple


# ── Load golden CSV ────────────────────────────────────────────────────────────
_GOLDEN: Dict[str, str] = {}  # canonical name → Chinese description
_PATH = os.path.expanduser("~/Documents/linxisa.csv")
if os.path.exists(_PATH):
    try:
        with open(_PATH, encoding="gb2312", errors="replace") as _fh:
            for _row in _csv.reader(_fh):
                if len(_row) < 3:
                    continue
                # col[0-2]: GPR name | alias | description
                _n = _row[0].strip()
                _d = _row[2].strip()
                if _n.startswith("R") and _d:
                    _GOLDEN[_n] = _d
                # col[0-2]: GPR name | alias | description
                # col[5-8]: Tile register section
                _n = _row[5].strip()
                _d = _row[6].strip()
                if _n and _d:
                    _GOLDEN[_n] = _d
                _n = _row[7].strip()
                _d = _row[8].strip()
                if _n and _d:
                    _GOLDEN[_n] = _d
                # col[11-13]: Scalar block second-layer (TR/UR)
                _n = _row[11].strip()
                _d = _row[13].strip()
                if _n and _d:
                    _GOLDEN[_n] = _d
                # col[15-17]: Data block second-layer (VTR/etc) + IO + Loop + Mask
                #   Rows with VTR/VUR/VMR/VNR names → data block
                #   Rows with RI/RO/LB/LC/P names → IO / Loop / Mask
                _n = _row[15].strip()
                _d = _row[17].strip()
                if _n and _d:
                    _GOLDEN[_n] = _d
    except Exception:
        pass


# ── Register table ───────────────────────────────────────────────────────────
# (section_label, [(canonical_name, preferred_asm, [aliases])])
_REGS: List[Tuple[str, List[Tuple[str, str, List[str]]]]] = [
    ("General-Purpose Registers (GPR)", [
        ("R0",  "zero",  ["zero", "r0"]),
        ("R1",  "sp",    ["sp", "r1"]),
        ("R2",  "a0",    ["a0", "r2"]),
        ("R3",  "a1",    ["a1", "r3"]),
        ("R4",  "a2",    ["a2", "r4"]),
        ("R5",  "a3",    ["a3", "r5"]),
        ("R6",  "a4",    ["a4", "r6"]),
        ("R7",  "a5",    ["a5", "r7"]),
        ("R8",  "a6",    ["a6", "r8"]),
        ("R9",  "a7",    ["a7", "r9"]),
        ("R10", "ra",    ["ra", "r10"]),
        ("R11", "s0",    ["s0", "r11", "fp"]),
        ("R12", "s1",    ["s1", "r12"]),
        ("R13", "s2",    ["s2", "r13"]),
        ("R14", "s3",    ["s3", "r14"]),
        ("R15", "s4",    ["s4", "r15"]),
        ("R16", "s5",    ["s5", "r16"]),
        ("R17", "s6",    ["s6", "r17"]),
        ("R18", "s7",    ["s7", "r18"]),
        ("R19", "s8",    ["s8", "r19"]),
        ("R20", "x0",    ["x0", "r20"]),
        ("R21", "x1",    ["x1", "r21"]),
        ("R22", "x2",    ["x2", "r22"]),
        ("R23", "x3",    ["x3", "r23"]),
    ]),
    ("Tile Registers (T#/U#/M#/N#)", [
        *[(f"T#{i}",  f"t#{i}",  [f"t#{i}"])  for i in range(1, 17)],
        *[(f"U#{i}",  f"u#{i}",  [f"u#{i}"])  for i in range(1, 17)],
        *[(f"M#{i}",  f"m#{i}",  [f"m#{i}"])  for i in range(1, 17)],
        *[(f"N#{i}",  f"n#{i}",  [f"n#{i}"])  for i in range(1, 17)],
    ]),
    ("Special: ACC and S", [
        ("ACC", "acc", ["acc"]),
        ("S",   "s",   ["s"]),
    ]),
    ("Scalar Block Layer-2 Aliases", [
        ("TR1", "tr1", ["t#1"]),  ("TR2", "tr2", ["t#2"]),
        ("TR3", "tr3", ["t#3"]),  ("TR4", "tr4", ["t#4"]),
        ("UR1", "ur1", ["u#1"]),  ("UR2", "ur2", ["u#2"]),
        ("UR3", "ur3", ["u#3", "u"]),  ("UR4", "ur4", ["u#4", "t"]),
    ]),
    ("Data Block Layer-2 Aliases", [
        ("VTR1", "vtr1", ["vt#1"]),  ("VTR2", "vtr2", ["vt#2"]),
        ("VTR3", "vtr3", ["vt#3"]),  ("VTR4", "vtr4", ["vt#4"]),
        ("VUR1", "vur1", ["vu#1"]),  ("VUR2", "vur2", ["vu#2"]),
        ("VUR3", "vur3", ["vu#3"]),  ("VUR4", "vur4", ["vu#4"]),
        ("VMR1", "vmr1", ["vm#1"]),  ("VMR2", "vmr2", ["vm#2"]),
        ("VMR3", "vmr3", ["vm#3"]),  ("VMR4", "vmr4", ["vm#4"]),
        ("VNR1", "vnr1", ["vn#1"]),  ("VNR2", "vnr2", ["vn#2"]),
        ("VNR3", "vnr3", ["vn#3"]),  ("VNR4", "vnr4", ["vn#4"]),
    ]),
    ("IO Parameters (Shader-Kernel Canonical)", [
        ("RI0",  "ri0",  ["ri0"]),   ("RI1",  "ri1",  ["ri1"]),
        ("RI2",  "ri2",  ["ri2"]),   ("RI3",  "ri3",  ["ri3"]),
        ("RI4",  "ri4",  ["ri4"]),   ("RI5",  "ri5",  ["ri5"]),
        ("RI6",  "ri6",  ["ri6"]),   ("RI7",  "ri7",  ["ri7"]),
        ("RI8",  "ri8",  ["ri8"]),   ("RI9",  "ri9",  ["ri9"]),
        ("RI10", "ri10", ["ri10"]),  ("RI11", "ri11", ["ri11"]),
        ("RO0",  "ro0",  ["ro0"]),   ("RO1",  "ro1",  ["ro1"]),
        ("RO2",  "ro2",  ["ro2"]),   ("RO3",  "ro3",  ["ro3"]),
    ]),
    ("Loop Control", [
        ("LB0", "lb0", ["lb0"]),  ("LB1", "lb1", ["lb1"]),  ("LB2", "lb2", ["lb2"]),
        ("LC0", "lc0", ["lc0"]),  ("LC1", "lc1", ["lc1"]),  ("LC2", "lc2", ["lc2"]),
    ]),
    ("EXEC Mask", [
        ("P", "p", ["p"]),
    ]),
]


def _anchor(label: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return f"reg5-{s}"


def generate(out_path: str) -> int:
    lines: List[str] = []
    lines.append("// Generated file; do not edit by hand.")
    lines.append("// Source: ~/Documents/linxisa.csv (golden contract)")
    lines.append("")

    code = 0
    total = 0
    for label, entries in _REGS:
        lines.append(f"[[{_anchor(label)}]]")
        lines.append(f"==== {label}")
        lines.append("")
        lines.append('[cols="1,1,2,4",options="header"]')
        lines.append("|===")
        lines.append("|Code |Name |Preferred asm |Description")
        lines.append("")

        for name, asm, aliases in entries:
            desc = _GOLDEN.get(name, "")
            aliases_s = ", ".join(aliases)
            lines.append(f"|`{code}`")
            lines.append(f"|`{name}`")
            lines.append(f"|`{asm}`")
            if desc:
                lines.append(f"|{desc}  __({aliases_s})__")
            else:
                lines.append(f"|__({aliases_s})__")
            code += 1
            total += 1

        lines.append("|===")
        lines.append("")

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return total


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate registers_reg5.adoc from golden CSV")
    ap.add_argument("--out-dir",
                   default="docs/architecture/isa-manual/src/generated")
    args = ap.parse_args()
    out = os.path.join(args.out_dir, "registers_reg5.adoc")
    n = generate(out)
    print(f"Wrote {out}  ({n} registers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
