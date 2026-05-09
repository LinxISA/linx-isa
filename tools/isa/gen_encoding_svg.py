#!/usr/bin/env python3
"""
SVG Bitfield Diagram Generator for LinxISA v0.56.

Produces professional instruction-encoding diagrams as inline SVG.
Used by the AsciiDoc ISA manual via the ``image`` macro:

    image::../generated/encodings/enc_add.svg[opts="width=800"]

Color coding (consistent across diagrams):
    green  = destination register (Rd, RegDst)
    blue   = first source register (Rs1, SrcL)
    teal   = second source register (Rs2, SrcR)
    orange = third source / extra operand (Rs3, SrcD, SrcA)
    purple = opcode / funct fields
    pink   = shift amount
    red    = immediate values
    gray   = zeroed / reserved constants

Usage:
    python3 gen_encoding_svg.py \\
        --spec isa/v0.56/linxisa-v0.56.json \\
        --out-dir docs/architecture/isa-manual/src/generated/encodings
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from typing import Any


# ── Palette ──────────────────────────────────────────────────────────────────
# These must match the CSS colours used in the SVG rectangles and text.
C = {
    "rd":       "#2E7D32",   # dark green  — destination register
    "regdst":   "#2E7D32",
    "rs1":      "#1565C0",   # blue        — first source register
    "srcl":     "#1565C0",
    "rs2":      "#00796B",   # teal        — second source register
    "srcr":     "#00796B",
    "rs3":      "#E65100",   # deep orange — third source / FMA operand
    "srcd":     "#E65100",
    "srca":     "#E65100",
    "funct3":   "#6A1B9A",   # purple     — funct3 / rounding mode
    "funct7":   "#5E35B1",   # violet     — funct7
    "opcode":   "#7B1FA2",   # violet-purple — opcode / funct12
    "shamt":    "#AD1457",   # pink        — shift amount
    "imm":      "#C62828",   # red         — immediate / offset
    "uimm":     "#C62828",
    "simm":     "#C62828",
    "offset":   "#C62828",
    "pred":     "#00695C",   # dark teal  — fence.pred
    "succ":     "#00695C",   # dark teal  — fence.succ
    "zero":     "#90A4AE",   # gray        — zeroed constant (reserved)
    "const":    "#607D8B",   # blue-gray   — non-zero constant
    "label":    "#333333",   # near-black  — text on white
    "bpos":     "#999999",   # light gray  — bit-position numbers
    "mnem":     "#1a1a1a",   # dark        — mnemonic heading
    "note":     "#aaaaaa",   # mid-gray    — bottom note
}


# ── Layout constants ──────────────────────────────────────────────────────────
W        = 900     # SVG viewport width
H_SINGLE = 68      # SVG height for a single-part instruction
H_TWO    = 132     # SVG height for a two-part instruction
ML       = 6       # left margin
MR       = 6       # right margin
MTOP     = 24      # top margin (room for mnemonic + bit labels)
MBOT     = 22      # bottom margin (room for length note)
FH       = 28      # field-row height


# ── Colour helper ─────────────────────────────────────────────────────────────

def _color(token: str, name: str, const: dict | None) -> str:
    """Return the CSS colour for a named (non-const) field token."""
    if const is not None:
        val = int(const["value"])
        return C["zero"] if val == 0 else C["const"]
    low = (token + name).lower()
    if name.lower() in ("rd", "regdst"):
        return C["rd"]
    if "rs1" in low or "srcl" in low or name.lower() == "srcl":
        return C["rs1"]
    if "rs2" in low or "srcr" in low or name.lower() == "srcr":
        return C["rs2"]
    if "rs3" in low or "srcd" in low or "srca" in low:
        return C["rs3"]
    if "shamt" in low:
        return C["shamt"]
    if any(k in low for k in ("funct3", "funct7", "funct12", "opcode",
                               "rst_type", "rra_type", "rld_type", "rounding", "rm",
                               "aq", "rl", "lr", "sc", "dr", "far")):
        return C["funct3"]
    if any(k in low for k in ("imm", "uimm", "simm", "offset", "pcr", "pred", "succ")):
        return C["imm"]
    return C["const"]


# ── Label helper ──────────────────────────────────────────────────────────────

def _label(token: str, const: dict | None, width: int) -> str:
    """Short display label for a field segment."""
    if const is not None:
        val = int(const["value"])
        if val == 0:
            return ""
        w = int(const["width"])
        if w <= 4:
            return f"{val:0{w}b}"
        elif w <= 8:
            return f"0x{val:02X}"
        elif w <= 12:
            return f"0x{val:03X}"
        else:
            return f"0x{val:0{(w+3)//4}X}"
    # Shorten common register names
    short = {
        "RegDst": "rd", "SrcL": "rs1", "SrcR": "rs2",
        "SrcD": "rs3", "SrcA": "rs3", "SrcRType": "rt",
        "shamt": "sh",
    }
    if token in short:
        return short[token]
    if len(token) > 8:
        return token[:8]
    return token


# ── Field layout ──────────────────────────────────────────────────────────────

@dataclass
class Field:
    name: str          # token string
    msb: int           # MSB bit index (31 for a 32-bit word)
    lsb: int           # LSB bit index (inclusive)
    color: str         # CSS colour
    label: str         # display text

    @property
    def bits(self) -> int:
        return self.msb - self.lsb + 1


@dataclass
class Part:
    width_bits: int
    fields: list[Field]

    @property
    def total_bits(self) -> int:
        return self.width_bits


def _build_parts(inst: dict[str, Any]) -> list[Part]:
    """Parse a linxisa JSON instruction into ordered Part + Field lists."""
    parts: list[Part] = []
    for part in inst.get("parts", []):
        w_bits = int(part.get("width_bits", 32))
        part_fields: list[Field] = []
        for seg in part.get("segments", []):
            msb = int(seg["msb"])
            lsb = int(seg["lsb"])
            token = seg.get("token", "")
            const = seg.get("const")
            name = seg.get("name", "")
            part_fields.append(Field(
                name=token,
                msb=msb,
                lsb=lsb,
                color=_color(token, name, const),
                label=_label(token, const, msb - lsb + 1),
            ))
        parts.append(Part(width_bits=w_bits, fields=part_fields))
    return parts


# ── SVG builder ───────────────────────────────────────────────────────────────

def _svg_for_parts(mnemonic: str, parts: list[Part], total_bits: int | None = None) -> str:
    """Build a complete SVG for one or two instruction parts."""
    if total_bits is None:
        total_bits = sum(p.width_bits for p in parts)

    n_parts = len(parts)
    H = H_TWO if n_parts == 2 else H_SINGLE
    AW = W - ML - MR                          # available width in pixels
    PX = AW / total_bits                       # pixels per bit

    rows: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        "  <defs>",
        "    <style>",
        "      text { font-family: 'Courier New', monospace; }",
        "    </style>",
        "  </defs>",
        f'  <text x="{ML}" y="15" font-family="Helvetica Neue,Arial,sans-serif" font-weight="bold" font-size="14" fill="{C["mnem"]}">{mnemonic}</text>',
    ]

    # ── Bit position labels ──────────────────────────────────────────────
    for i in range(total_bits):
        pos = total_bits - 1 - i    # MSB down to LSB
        if pos % 4 == 0 or pos == total_bits - 1:
            x = ML + (i + 0.5) * PX
            rows.append(f'  <text x="{x:.2f}" y="8" text-anchor="middle" font-size="8" fill="{C["bpos"]}">{pos}</text>')

    # ── Field rectangles + labels (one row per part) ────────────────────
    for p_idx, part in enumerate(parts):
        row_y = MTOP + p_idx * (FH + 6)
        px_per_bit = AW / part.width_bits

        # Outer border
        rows.append(
            f'  <rect x="{ML}" y="{row_y}" width="{AW:.2f}" height="{FH}"'
            f' fill="none" stroke="{C["bpos"]}" stroke-width="0.8"/>'
        )

        for fld in part.fields:
            # Field rectangle
            left  = ML + (part.width_bits - 1 - fld.msb) * px_per_bit
            right = ML + (part.width_bits - 1 - fld.lsb + 1) * px_per_bit
            fw = right - left
            rows.append(
                f'  <rect x="{left:.3f}" y="{row_y+1}" width="{fw:.3f}" height="{FH-2}"'
                f' fill="{fld.color}" stroke="white" stroke-width="0.5"/>'
            )
            # Field label (centered)
            if fld.label and fw > 12:
                cx = left + fw / 2
                cy = row_y + FH / 2 + 3.5
                # Truncate if needed
                label = fld.label
                max_chars = max(1, int(fw / 6.5))
                if len(label) > max_chars:
                    label = label[:max_chars - 1] + "\u2026"
                rows.append(
                    f'  <text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle"'
                    f' dominant-baseline="middle" font-size="8.5" fill="white"'
                    f' pointer-events="none">{label}</text>'
                )

        # Part label on the right
        part_label = f"[{part.width_bits - 1}:0]" if n_parts == 2 else ""
        if part_label:
            rows.append(
                f'  <text x="{ML + AW + 2}" y="{row_y + FH/2 + 4}"'
                f' font-size="8" fill="{C["bpos"]}" font-family="Helvetica Neue,Arial">{part_label}</text>'
            )

    # ── Bottom note ─────────────────────────────────────────────────────
    rows.append(
        f'  <text x="{ML}" y="{H - 4}" font-size="9" fill="{C["note"]}"'
        f' font-family="Helvetica Neue,Arial,sans-serif">{total_bits}-bit encoding</text>'
    )

    rows.append("</svg>")
    return "\n".join(rows)


# ── Colour legend ─────────────────────────────────────────────────────────────

LEGEND_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 80" width="480" height="80">
  <text x="0" y="12" font-family="Helvetica Neue,Arial" font-weight="bold" font-size="11" fill="#1a1a1a">Field colour key</text>
  <rect x="0"   y="18" width="14" height="12" fill="{rd}"      rx="1"/><text x="18"  y="28" font-size="9" fill="#333">Rd / RegDst (destination)</text>
  <rect x="175" y="18" width="14" height="12" fill="{rs1}"     rx="1"/><text x="193" y="28" font-size="9" fill="#333">Rs1 / SrcL (1st source)</text>
  <rect x="330" y="18" width="14" height="12" fill="{rs2}"     rx="1"/><text x="348" y="28" font-size="9" fill="#333">Rs2 / SrcR (2nd source)</text>
  <rect x="0"   y="34" width="14" height="12" fill="{rs3}"     rx="1"/><text x="18"  y="44" font-size="9" fill="#333">Rs3 / SrcD (3rd source)</text>
  <rect x="175" y="34" width="14" height="12" fill="{funct3}"  rx="1"/><text x="193" y="44" font-size="9" fill="#333">funct / opcode</text>
  <rect x="330" y="34" width="14" height="12" fill="{shamt}"   rx="1"/><text x="348" y="44" font-size="9" fill="#333">shamt</text>
  <rect x="0"   y="50" width="14" height="12" fill="{imm}"     rx="1"/><text x="18"  y="60" font-size="9" fill="#333">imm / offset</text>
  <rect x="175" y="50" width="14" height="12" fill="{pred}"    rx="1"/><text x="193" y="60" font-size="9" fill="#333">fence.pred / succ</text>
  <rect x="330" y="50" width="14" height="12" fill="{zero}"   rx="1"/><text x="348" y="60" font-size="9" fill="#333">reserved / const(0)</text>
</svg>""".format(**C)


# ── Slug helper ──────────────────────────────────────────────────────────────

def _slug(mnemonic: str) -> str:
    s = mnemonic.strip().lower()
    s = s.replace(".", "_").replace(" ", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_") or "inst"


# ── Main ──────────────────────────────────────────────────────────────────────

def generate_all(spec_path: str, out_dir: str) -> int:
    """Generate SVG encoding diagrams for every instruction in the catalog."""
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    os.makedirs(out_dir, exist_ok=True)

    count = 0
    for inst in spec.get("instructions", []):
        mnemonic = inst["mnemonic"]
        parts = _build_parts(inst)
        if not parts:
            continue

        total_bits = sum(p.width_bits for p in parts)
        svg = _svg_for_parts(mnemonic, parts, total_bits)

        if len(parts) == 1:
            path = os.path.join(out_dir, f"enc_{_slug(mnemonic)}.svg")
        else:
            path = os.path.join(out_dir, f"enc_{_slug(mnemonic)}_parts.svg")

        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        count += 1

    # Also write the colour legend once
    legend_path = os.path.join(out_dir, "encoding_legend.svg")
    with open(legend_path, "w", encoding="utf-8") as fh:
        fh.write(LEGEND_SVG)

    sys.stderr.write(f"Generated {count + 1} SVGs in {out_dir}\n")
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="SVG bitfield diagram generator for LinxISA")
    ap.add_argument("--spec", default="isa/v0.56/linxisa-v0.56.json")
    ap.add_argument("--out-dir",
                   default="docs/architecture/isa-manual/src/generated/encodings")
    args = ap.parse_args()
    n = generate_all(args.spec, args.out_dir)
    return 0 if n > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
