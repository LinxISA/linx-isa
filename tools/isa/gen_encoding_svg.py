#!/usr/bin/env python3
"""
SVG Bitfield Diagram Generator for LinxISA Instruction Encoding

This script generates professional SVG visualizations of instruction bitfields
for inclusion in the ISA manual. It creates clean, readable diagrams showing
the bit layout of each instruction encoding.

Usage:
    python3 gen_encoding_svg.py --spec isa/v0.3/linxisa-v0.3.json --out-dir docs/architecture/isa-manual/src/generated/encodings
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


# Color scheme for different field types
COLORS = {
    "opcode": "#4A90D9",      # Blue
    "rd": "#5CB85C",          # Green
    "rs1": "#F0AD4E",         # Orange
    "rs2": "#F0AD4E",         # Orange  
    "rs3": "#F0AD4E",         # Orange
    "imm": "#D9534F",         # Red
    "funct3": "#9B59B6",      # Purple
    "funct7": "#9B59B6",     # Purple
    "funct12": "#9B59B6",    # Purple
    "csr": "#E91E63",         # Pink
    "default": "#95A5A6",     # Gray
    "reserved": "#BDC3C7",    # Light gray
    "empty": "#ECF0F1",       # Very light gray
}


@dataclass
class BitField:
    """Represents a single bitfield in an instruction encoding."""
    name: str
    start_bit: int  # MSB position (0-indexed from left)
    end_bit: int    # LSB position
    field_type: str = "default"
    
    @property
    def width(self) -> int:
        return self.end_bit - self.start_bit + 1


@dataclass 
class InstructionEncoding:
    """Represents an instruction's encoding information."""
    mnemonic: str
    length: int  # in bits
    fields: List[BitField]
    opcode_value: Optional[int] = None


def parse_instruction_fields(inst: Dict[str, Any], part_index: int = 0) -> List[BitField]:
    """Parse instruction fields from the JSON catalog."""
    fields = []
    
    parts = inst.get("parts", [])
    if part_index >= len(parts):
        return fields
        
    part = parts[part_index]
    segments = part.get("segments", [])
    
    for seg in segments:
        field_name = seg.get("name", "unknown")
        bit_range = seg.get("bit_range", {})
        start = bit_range.get("msb", 0)
        end = bit_range.get("lsb", 0)
        
        # Determine field type for coloring
        field_type = "default"
        lower_name = field_name.lower()
        
        if "opcode" in lower_name:
            field_type = "opcode"
        elif lower_name in ("rd", "regdst"):
            field_type = "rd"
        elif lower_name in ("rs1", "srcl"):
            field_type = "rs1"
        elif lower_name in ("rs2", "srcr"):
            field_type = "rs2"
        elif lower_name in ("rs3", "srcd"):
            field_type = "rs3"
        elif "imm" in lower_name or lower_name.startswith("uimm") or lower_name.startswith("simm"):
            field_type = "imm"
        elif lower_name.startswith("funct"):
            field_type = "funct3" if start >= 12 else "funct7"
        elif "csr" in lower_name:
            field_type = "csr"
            
        fields.append(BitField(field_name, start, end, field_type))
    
    return fields


def generate_svg(encoding: InstructionEncoding, width: int = 800, height: int = 120) -> str:
    """Generate SVG diagram for an instruction encoding."""
    
    bits = encoding.length
    if bits not in (16, 32, 48, 64):
        bits = 32  # Default to 32-bit
    
    # SVG dimensions
    margin_left = 60
    margin_right = 20
    margin_top = 30
    margin_bottom = 40
    
    field_width = (width - margin_left - margin_right) / bits
    row_height = (height - margin_top - margin_bottom) / 2
    
    # Generate SVG
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '  <defs>',
        '    <style>',
        '      .field-label { font-family: "Courier New", monospace; font-size: 11px; fill: #333; }',
        '      .bit-label { font-family: "Courier New", monospace; font-size: 9px; fill: #666; text-anchor: middle; }',
        '      .mnemonic { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #333; }',
        '      .field-rect { stroke: #fff; stroke-width: 1px; }',
        '    </style>',
        '  </defs>',
        '',
        f'  <text x="10" y="20" class="mnemonic">{encoding.mnemonic}</text>',
        f'  <text x="10" y="{height - 10}" class="mnemonic" fill="#666">{bits}-bit</text>',
        ''
    ]
    
    # Draw bit positions (show every 4 bits for readability)
    for i in range(0, bits, 4):
        x = margin_left + (i + 0.5) * field_width
        bit_pos = bits - 1 - i
        svg_lines.append(f'  <text x="{x}" y="{margin_top - 8}" class="bit-label">{bit_pos}</text>')
    
    # Draw the encoding row
    y = margin_top + row_height / 2
    
    # Group fields by their positions and draw rectangles
    sorted_fields = sorted(encoding.fields, key=lambda f: f.start_bit, reverse=True)
    
    for field in sorted_fields:
        # Convert MSB:LSB to left:right positions (MSB is on the left)
        left_pos = bits - 1 - field.start_bit
        right_pos = bits - 1 - field.end_bit
        
        x_left = margin_left + left_pos * field_width
        x_right = margin_left + (right_pos + 1) * field_width
        field_w = x_right - x_left
        
        color = COLORS.get(field.field_type, COLORS["default"])
        
        # Draw field rectangle
        svg_lines.append(
            f'  <rect x="{x_left}" y="{y}" width="{field_w}" height="{row_height}" '
            f'fill="{color}" class="field-rect" rx="3"/>'
        )
        
        # Draw field name centered in the rectangle
        if field_w > 30:
            label_x = x_left + field_w / 2
            label_y = y + row_height / 2 + 4
            svg_lines.append(
                f'  <text x="{label_x}" y="{label_y}" class="field-label" '
                f'text-anchor="middle">{field.name}</text>'
            )
    
    # Draw the horizontal line
    svg_lines.append(
        f'  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left + bits * field_width}" y2="{margin_top}" '
        'stroke="#333" stroke-width="2"/>'
    )
    svg_lines.append(
        f'  <line x1="{margin_left}" y1="{margin_top + row_height}" x2="{margin_left + bits * field_width}" y2="{margin_top + row_height}" '
        'stroke="#333" stroke-width="2"/>'
    )
    
    svg_lines.append('</svg>')
    
    return '\n'.join(svg_lines)


def generate_encoding_diagrams(spec_path: str, output_dir: str) -> int:
    """Generate SVG diagrams for all instructions in the spec."""
    
    # Read the specification
    with open(spec_path, 'r') as f:
        spec = json.load(f)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    count = 0
    
    # Process each instruction
    instructions = spec.get("instructions", [])
    
    # Group by format for better organization
    formats: Dict[str, List[Dict]] = {}
    
    for inst in instructions:
        mnemonic = inst.get("mnemonic", "UNKNOWN")
        
        # Get encoding length
        parts = inst.get("parts", [])
        if not parts:
            continue
            
        total_bits = sum(p.get("length", 32) for p in parts)
        
        # Generate SVG for each part
        for part_idx, part in enumerate(parts):
            fields = parse_instruction_fields(inst, part_idx)
            
            # Create filename from mnemonic
            safe_name = mnemonic.replace(".", "_").replace(" ", "_").lower()
            if len(parts) > 1:
                safe_name += f"_part{part_idx + 1}"
            
            encoding = InstructionEncoding(
                mnemonic=mnemonic,
                length=part.get("length", 32),
                fields=fields
            )
            
            svg = generate_svg(encoding)
            
            # Write SVG file
            svg_path = os.path.join(output_dir, f"enc_{safe_name}.svg")
            with open(svg_path, 'w') as f:
                f.write(svg)
            
            count += 1
    
    print(f"Generated {count} SVG encoding diagrams in {output_dir}")
    return count


def generate_format_summary(spec_path: str, output_path: str) -> int:
    """Generate a summary of all instruction formats."""
    
    with open(spec_path, 'r') as f:
        spec = json.load(f)
    
    formats: Dict[str, Dict] = {}
    
    for inst in spec.get("instructions", []):
        for part_idx, part in enumerate(inst.get("parts", [])):
            decode = part.get("decode", "Unknown")
            
            if decode not in formats:
                formats[decode] = {
                    "count": 0,
                    "length": part.get("length", 32),
                    "fields": []
                }
            
            formats[decode]["count"] += 1
            
            # Collect field info
            for seg in part.get("segments", []):
                field_name = seg.get("name", "unknown")
                if field_name not in formats[decode]["fields"]:
                    formats[decode]["fields"].append(field_name)
    
    # Generate AsciiDoc table
    lines = [
        "// Generated file; do not edit by hand.",
        "",
        "[[encoding-format-summary]]",
        "=== Instruction Format Summary",
        "",
        "[cols=\"1,1,1,3\",options=\"header\"]",
        "||===",
        "||Format |Bits |Count |Fields"
    ]
    
    for fmt, info in sorted(formats.items()):
        fields_str = ", ".join(info["fields"][:6])
        if len(info["fields"]) > 6:
            fields_str += f" ... ({len(info['fields'])} total)"
        lines.append(f"||`{fmt}` |{info['length']} |{info['count']} |{fields_str}")
    
    lines.append("||===")
    
    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Generated format summary with {len(formats)} formats at {output_path}")
    return len(formats)


def main():
    parser = argparse.ArgumentParser(description="Generate SVG bitfield diagrams for LinxISA")
    parser.add_argument("--spec", required=True, help="Path to linxisa JSON spec")
    parser.add_argument("--out-dir", required=True, help="Output directory for SVGs")
    parser.add_argument("--format-summary", help="Path for format summary AsciiDoc")
    
    args = parser.parse_args()
    
    # Generate encoding diagrams
    count = generate_encoding_diagrams(args.spec, args.out_dir)
    
    # Generate format summary if requested
    if args.format_summary:
        generate_format_summary(args.spec, args.format_summary)
    
    return 0 if count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
