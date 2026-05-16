#!/usr/bin/env python3
"""
WaveDrom SVG Generator for LinxISA v0.56 Instruction Encodings.

Converts LinxISA instruction definitions into WaveDrom JSON and renders them
as beautiful bitfield SVG diagrams via the WaveDrom Node.js library.

The output format is inspired by ARM DDI0500 and RISC-V ISA manual diagrams:
  - MSB on the left, LSB on the right
  - Color-coded fields (opcode=blue, rd=green, rs1=cyan, rs2=teal,
    rs3=orange, funct=purple, shamt=pink, imm=red, reserved=gray)
  - Bit position labels above each group of 4 bits
  - Mnemonic label in the top-left corner

Usage:
    python3 gen_wavedrom_svg.py \\
        --spec isa/v0.56/linxisa-v0.56.json \\
        --out-dir docs/isa/wavedrom \\
        --wavedrom tools/wavedrom

The SVG files are referenced by per-instruction markdown pages generated
by gen_isa_pages.py.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any


# ── WaveDrom palette (light pastels, inspired by WaveDrom default skin) ─────────
WD_PALETTE = {
    "opcode":  ("#7FB3D3", "#1A3A5C"),  # blue-slate / dark text
    "rd":      ("#82C77A", "#1A4A1C"),  # green / dark text
    "regdst":  ("#82C77A", "#1A4A1C"),
    "rs1":     ("#6EC9D8", "#1A3F47"),  # cyan / dark text
    "srcl":    ("#6EC9D8", "#1A3F47"),
    "rs2":     ("#5BBFAA", "#1A3A32"),  # teal / dark text
    "srcr":    ("#5BBFAA", "#1A3A32"),
    "rs3":     ("#E8976B", "#4A1A00"),  # orange / dark text
    "srcd":    ("#E8976B", "#4A1A00"),
    "srca":    ("#E8976B", "#4A1A00"),
    "funct3":  ("#B39DDB", "#2A1A4A"),  # purple / dark text
    "funct7":  ("#9C6FD4", "#2A1A3C"),
    "funct12": ("#9C6FD4", "#2A1A3C"),
    "opcode2": ("#7FB3D3", "#1A3A5C"),
    "shamt":   ("#E57399", "#4A1A2A"),  # pink / dark text
    "imm":     ("#F4A261", "#3A1A00"),  # amber / dark text
    "uimm":    ("#F4A261", "#3A1A00"),
    "simm":    ("#F4A261", "#3A1A00"),
    "offset":  ("#F4A261", "#3A1A00"),
    "pred":    ("#457B9D", "#0A1A25"),  # dark blue / light text
    "succ":    ("#457B9D", "#0A1A25"),
    "zero":    ("#E0E0E0", "#616161"),  # light gray / mid text
    "const":   ("#C8C8C8", "#424242"),  # gray / dark text
    "default": ("#D0D0D0", "#333333"),
    "mnem":    "#1A1A2E",              # near-black
    "bpos":    "#888888",              # bit-position numbers
    "note":    "#AAAAAA",              # bottom note
    "border":  "#555555",
}

# Fallback fills
_FILL_FUN = [
    "#B39DDB", "#6EC9D8", "#82C77A", "#F4A261",
    "#E57399", "#5BBFAA", "#7FB3D3", "#E8976B",
]


def _slug(mnemonic: str) -> str:
    s = mnemonic.strip().lower()
    s = re.sub(r"\.+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_") or "inst"


# ── Field colour helper ────────────────────────────────────────────────────────

def _field_color(token: str, name: str, const: dict | None) -> tuple[str, str]:
    """Return (fill, text_color) for a field."""
    if const is not None:
        val = int(const["value"])
        if val == 0:
            return WD_PALETTE["zero"]
        return WD_PALETTE["const"]

    t = (token + name).lower()
    if "rd" in t or "regdst" in t:
        return WD_PALETTE.get("rd", WD_PALETTE["default"])
    if "rs1" in t or "srcl" in t:
        return WD_PALETTE.get("rs1", WD_PALETTE["default"])
    if "rs2" in t or "srcr" in t:
        return WD_PALETTE.get("rs2", WD_PALETTE["default"])
    if "rs3" in t or "srcd" in t or "srca" in t:
        return WD_PALETTE.get("rs3", WD_PALETTE["default"])
    if "funct" in t or "opcode" in t or "rounding" in t or "rm" in t or "aq" in t or "rl" in t:
        return WD_PALETTE.get("funct3", WD_PALETTE["default"])
    if "shamt" in t:
        return WD_PALETTE.get("shamt", WD_PALETTE["default"])
    if any(k in t for k in ("imm", "uimm", "simm", "offset", "pcr", "pred", "succ")):
        return WD_PALETTE.get("imm", WD_PALETTE["default"])
    return WD_PALETTE["default"]


def _field_label(token: str, const: dict | None, width: int) -> str:
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


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class SegField:
    name: str
    msb: int
    lsb: int
    fill: str
    text_color: str
    label: str

    @property
    def bits(self) -> int:
        return self.msb - self.lsb + 1


# ── WaveDrom JSON builder ─────────────────────────────────────────────────────

def _build_wavedrom_config(
    mnemonic: str,
    parts: list[dict],
    svg_w: int,
) -> dict:
    """
    Build a WaveDrom config dict that produces a bitfield diagram.

    Structure mirrors the WaveDrom-on-Chip 'reg' type:
      config = { head: {...}, reg: {...}, save: [...] }
    """

    # Collect fields from all parts
    all_fields: list[SegField] = []
    part_starts = []
    total_bits = 0

    for p in parts:
        part_starts.append(total_bits)
        pw = int(p.get("width_bits", 32))
        total_bits += pw

        for seg in p.get("segments", []):
            msb = int(seg["msb"])
            lsb = int(seg["lsb"])
            token = seg.get("token", "")
            const = seg.get("const")
            name = seg.get("name", "")
            fill, tcolor = _field_color(token, name, const)
            label = _field_label(token, const, msb - lsb + 1)

            # Remap msb/lsb from part-relative to instruction-relative
            abs_msb = total_bits - p.get("segment_offset_bits", 0) - (int(p.get("width_bits", 32)) - 1 - msb)
            # Simpler: msb/lsb in the JSON are already part-relative (0 = LSB of that part)
            # But total_bits tracks instruction-relative. For a 32-bit part:
            #   part starts at bit (total_bits - pw)
            #   part-relative msb=31 maps to abs_msb = (total_bits - pw) + 31
            #   part-relative lsb=0 maps to abs_lsb = (total_bits - pw)
            # Actually the msb/lsb in the JSON are already absolute within the part
            # Let's just keep them and note the part offset
            all_fields.append(SegField(
                name=token, msb=msb, lsb=lsb,
                fill=fill, text_color=tcolor, label=label
            ))

    n_parts = len(parts)
    # Per-part pixel widths
    part_pw = []
    for i, p in enumerate(parts):
        pw = int(p.get("width_bits", 32))
        part_pw.append(pw)

    # reg[] for WaveDrom: each row is a "register" (part), each cell is a field
    # WaveDrom reg layout: left=MSB, right=LSB
    reg_rows = []
    for p_idx, p in enumerate(parts):
        pw = part_pw[p_idx]
        cells = []
        # Sort fields by msb descending (MSB first = leftmost in WaveDrom)
        fields = sorted(
            [f for f in all_fields if f.msb <= pw - 1 and f.lsb >= 0],
            key=lambda x: -x.msb
        )
        for f in fields:
            cells.append({
                "bits": f.bits,
                "name": f.label,
                "attr": [f.name],
                # We'll handle colour via config.fill
            })
        reg_rows.append(cells)

    # config.fill maps field name patterns to colours
    fill_map: list[dict] = []
    seen_fills: set[str] = set()
    for f in all_fields:
        key = f.name
        if key not in seen_fills:
            seen_fills.add(key)
            fill_map.append({
                "name": key,
                "fill": f.fill,
            })

    config = {
        "head": {
            "text": mnemonic,
            "debit": True,
            "comment": f"{total_bits}-bit",
        },
        "config": {
            "h": 10,
            "fontsize": 11,
            "fontfamily": "Courier New",
            "textpos": "t",
            "edges": ["left", "right"],
            "fill": fill_map,
        },
        "reg": reg_rows,
    }
    return config


# ── SVG renderer (pure Python fallback) ────────────────────────────────────────

def _render_svg_fallback(mnemonic: str, parts: list[dict], total_bits: int) -> str:
    """Render a bitfield SVG directly in Python when WaveDrom JS is unavailable."""

    n_parts = len(parts)
    svg_w = min(960, 100 + total_bits * 14)
    svg_h = 68 if n_parts == 1 else 128
    ml, mr = 10, 10
    mt, mb = 28, 26
    fh = svg_h - mt - mb          # field row height
    aw = svg_w - ml - mr

    rows = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">',
        f'  <defs><style>text{{font-family:"Courier New",monospace}}</style></defs>',
        f'  <text x="{ml}" y="17" font-family="Helvetica Neue,Arial" font-weight="bold" font-size="14" fill="{WD_PALETTE["mnem"]}">{mnemonic}</text>',
    ]

    # Bit position labels every 4 bits
    px_per_bit = aw / total_bits
    for i in range(total_bits):
        pos = total_bits - 1 - i
        if pos % 4 == 0 or pos == total_bits - 1:
            x = ml + (i + 0.5) * px_per_bit
            rows.append(f'  <text x="{x:.2f}" y="9" text-anchor="middle" font-size="8" fill="{WD_PALETTE["bpos"]}">{pos}</text>')

    part_offsets = []
    offset = 0
    for p in parts:
        part_offsets.append(offset)
        offset += int(p.get("width_bits", 32))

    for p_idx, p in enumerate(parts):
        pw = int(p.get("width_bits", 32))
        row_y = mt + p_idx * (fh + 6)
        px_pb = aw / pw   # pixels per bit for this part

        # Outer border rect
        rows.append(
            f'  <rect x="{ml}" y="{row_y}" width="{aw:.2f}" height="{fh}"'
            f' fill="none" stroke="{WD_PALETTE["border"]}" stroke-width="0.8"/>'
        )

        # Parse and render segments
        for seg in p.get("segments", []):
            msb = int(seg["msb"])
            lsb = int(seg["lsb"])
            token = seg.get("token", "")
            const = seg.get("const")
            name = seg.get("name", "")
            fill, tcolor = _field_color(token, name, const)
            label = _field_label(token, const, msb - lsb + 1)

            # Convert to absolute bit positions in the whole instruction
            abs_offset = part_offsets[p_idx]
            abs_msb = abs_offset + msb
            abs_lsb = abs_offset + lsb

            # Map to pixel positions on the SVG
            # Bit total_bits-1 maps to x=ml, bit 0 maps to x=ml+aw
            left_x = ml + (total_bits - 1 - abs_msb) * px_per_bit
            right_x = ml + (total_bits - abs_lsb) * px_per_bit
            fw = right_x - left_x

            rows.append(
                f'  <rect x="{left_x:.3f}" y="{row_y+1}" width="{fw:.3f}" height="{fh-2}"'
                f' fill="{fill}" stroke="white" stroke-width="0.5" rx="1"/>'
            )
            if label and fw > 14:
                cx = left_x + fw / 2
                cy = row_y + fh / 2 + 3.5
                max_chars = max(1, int(fw / 6.5))
                disp_label = label if len(label) <= max_chars else label[:max_chars-1] + "\u2026"
                rows.append(
                    f'  <text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle"'
                    f' dominant-baseline="middle" font-size="8.5" fill="{tcolor}"'
                    f' pointer-events="none">{disp_label}</text>'
                )

        # Part label on right
        if n_parts > 1:
            plabel = f"[{pw - 1}:0]"
            rows.append(
                f'  <text x="{ml + aw + 3}" y="{row_y + fh/2 + 4}"'
                f' font-size="8" fill="{WD_PALETTE["bpos"]}" font-family="Helvetica Neue,Arial">{plabel}</text>'
            )

    rows.append(
        f'  <text x="{ml}" y="{svg_h - 5}" font-size="9" fill="{WD_PALETTE["note"]}"'
        f' font-family="Helvetica Neue,Arial,sans-serif">{total_bits}-bit encoding</text>'
    )
    rows.append("</svg>")
    return "\n".join(rows)


# ── WaveDrom Node.js renderer ─────────────────────────────────────────────────

_WAVEDROM_JS = """
const fs = require('fs');
const path = require('path');

// Get input JSON from stdin or first argument
let input;
if (process.argv.length > 2) {
    input = fs.readFileSync(process.argv[2], 'utf8');
} else {
    input = fs.readSync(0, 'utf8');
}

const config = JSON.parse(input);

// Load WaveDrom
let WaveDrom;
try {
    WaveDrom = require('wavedrom');
} catch(e) {
    // Try from tools/wavedrom/node_modules
    const altPath = path.join(__dirname, 'node_modules', 'wavedrom');
    if (fs.existsSync(altPath)) {
        WaveDrom = require(altPath);
    } else {
        console.error('WaveDrom not found');
        process.exit(1);
    }
}

// Use WaveDrom's renderAny for reg diagrams
const svg = WaveDrom.renderAny(config);

process.stdout.write(svg);
"""


def _call_wavedrom(config: dict) -> str | None:
    """Call WaveDrom Node.js renderer. Returns SVG string or None on failure."""
    try:
        wavedrom_dir = os.path.join(os.getcwd(), "tools", "wavedrom")
        proc = subprocess.run(
            ["node", "-e", _WAVEDROM_JS],
            input=json.dumps(config),
            capture_output=True,
            text=True,
            cwd=wavedrom_dir,
            timeout=30,
        )
        if proc.returncode == 0:
            return proc.stdout
    except (subprocess.TimeoutExpired, OSError) as e:
        sys.stderr.write(f"WaveDrom call failed: {e}\n")
    return None


# ── Main generation ────────────────────────────────────────────────────────────

def generate_wavedrom_svgs(
    spec_path: str,
    out_dir: str,
    wavedrom_dir: str | None = None,
) -> int:
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    os.makedirs(out_dir, exist_ok=True)

    # Group instructions by mnemonic; keep first form as canonical
    from collections import OrderedDict
    mnem_map: dict[str, dict] = OrderedDict()
    for inst in spec.get("instructions", []):
        m = inst["mnemonic"]
        if m not in mnem_map:
            mnem_map[m] = inst

    count = 0
    skipped = 0

    for mnemonic, inst in mnem_map.items():
        parts = inst.get("parts", [])
        if not parts:
            skipped += 1
            continue

        total_bits = sum(int(p.get("width_bits", 32)) for p in parts)

        # Try WaveDrom first
        svg_out: str | None = None
        config = _build_wavedrom_config(mnemonic, parts, min(960, 100 + total_bits * 14))

        if wavedrom_dir and os.path.exists(os.path.join(wavedrom_dir, "node_modules", "wavedrom")):
            wd_svg = _call_wavedrom(config)
            if wd_svg:
                svg_out = _wrap_wavedrom_svg(wd_svg, mnemonic, total_bits)

        # Fall back to Python renderer
        if svg_out is None:
            svg_out = _render_svg_fallback(mnemonic, parts, total_bits)

        # Save
        slug = _slug(mnemonic)
        n_parts = len(parts)
        if n_parts > 1:
            slug += "_parts"
        path_svg = os.path.join(out_dir, f"enc_{slug}.svg")
        with open(path_svg, "w", encoding="utf-8") as fh:
            fh.write(svg_out)
        count += 1

    # Also write a legend
    legend = _render_legend()
    with open(os.path.join(out_dir, "encoding_legend.svg"), "w", encoding="utf-8") as fh:
        fh.write(legend)

    sys.stderr.write(
        f"Generated {count} WaveDrom SVGs + legend in {out_dir}"
        + (f" ({skipped} skipped)" if skipped else "")
        + "\n"
    )
    return count


def _wrap_wavedrom_svg(raw_svg: str, mnemonic: str, total_bits: int) -> str:
    """Post-process WaveDrom output to add mnemonic label and 32-bit note."""
    # WaveDrom outputs a full <svg>. We inject a background rect + labels.
    # The SVG already has a text element with the mnemonic from the config head.
    # Add the bit-length note at the bottom.
    note_y = 52 if raw_svg.count('<svg') == 1 else 80
    replacement = raw_svg.replace(
        "</svg>",
        f'  <text x="10" y="{note_y}" font-size="9" fill="#aaaaaa" font-family="Arial">'
        f"{total_bits}-bit encoding</text>\n</svg>"
    )
    return replacement


def _render_legend() -> str:
    """Render the field colour legend as an SVG."""
    W, H = 680, 72
    items = [
        ("#82C77A", "Rd / RegDst (destination register)"),
        ("#6EC9D8", "Rs1 / SrcL (1st source register)"),
        ("#5BBFAA", "Rs2 / SrcR (2nd source register)"),
        ("#E8976B", "Rs3 / SrcD (3rd source / FMA operand)"),
        ("#B39DDB", "funct / opcode (function/control field)"),
        ("#E57399", "shamt (shift amount)"),
        ("#F4A261", "imm / offset (immediate value)"),
        ("#E0E0E0", "reserved / const(0)"),
    ]
    rows = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        '  <style>text{font-family:"Helvetica Neue",Arial,sans-serif}</style>',
        '  <text x="0" y="14" font-weight="bold" font-size="11" fill="#1a1a1a">Field colour key</text>',
    ]
    for i, (color, label) in enumerate(items):
        col = i % 4
        row = i // 4
        x = col * 170
        y = 30 + row * 22
        rows.append(f'  <rect x="{x}" y="{y-11}" width="12" height="12" fill="{color}" rx="2"/>')
        rows.append(f'  <text x="{x+16}" y="{y}" font-size="9" fill="#333">{label}</text>')
    rows.append("</svg>")
    return "\n".join(rows)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="WaveDrom SVG bitfield generator for LinxISA v0.56"
    )
    ap.add_argument(
        "--spec", default="isa/v0.56/linxisa-v0.56.json",
        help="Path to linxisa-v*.json catalog",
    )
    ap.add_argument(
        "--out-dir", default="docs/isa/wavedrom",
        help="Output directory for SVG files",
    )
    ap.add_argument(
        "--wavedrom",
        default="tools/wavedrom",
        help="Path to WaveDrom npm package (tools/wavedrom)",
    )
    args = ap.parse_args()
    return 0 if generate_wavedrom_svgs(args.spec, args.out_dir, args.wavedrom) >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
