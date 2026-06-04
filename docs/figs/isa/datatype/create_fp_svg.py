#!/usr/bin/env python3
"""Generate FP format SVG diagrams (fp16, fp32, fp64, bf16, hf32, tf32)"""

import os

def create_svg_file(filepath, width, height, title, sign_bits, exp_bits, mant_bits, extra_label=""):
    """Create a floating-point format SVG diagram"""
    # Colors
    sign_color = "#808080"  # Gray
    exp_color = "#4169E1"   # Royal Blue
    mant_color = "#228B22"  # Forest Green

    # Calculate dimensions
    box_height = 80
    bit_width = 16
    total_bits = 1 + sign_bits + mant_bits

    extra_label_svg = f'<text x="{width//2}" y="{height-10}" text-anchor="middle" class="label">{extra_label}</text>' if extra_label else ''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>
    text {{ font-family: "Helvetica Neue", Arial, sans-serif; font-size: 14px; }}
    .title {{ font-size: 18px; font-weight: bold; fill: #333; }}
    .label {{ font-size: 12px; fill: #555; }}
    .bit {{ font-size: 11px; fill: #333; }}
  </style>

  <!-- Title -->
  <text x="10" y="25" class="title">{title}</text>

  <!-- Bit position labels -->
  <text x="10" y="50" class="label">31</text>
  <text x="{width-30}" y="50" class="label">0</text>
  <text x="{width//2}" y="50" class="label" text-anchor="middle">{total_bits-1}:0</text>

  <!-- Main bit boxes -->
  <g transform="translate(10, 60)">
    <!-- Sign bit -->
    <rect x="0" y="0" width="{bit_width}" height="{box_height}" fill="{sign_color}" rx="3" stroke="#333" stroke-width="1"/>
    <text x="{bit_width//2}" y="{box_height//2 + 5}" text-anchor="middle" fill="white" class="bit">S</text>
    <text x="{bit_width//2}" y="{box_height + 20}" text-anchor="middle" class="label">1</text>

    <!-- Exponent bits -->
    <rect x="{bit_width}" y="0" width="{bit_width * exp_bits}" height="{box_height}" fill="{exp_color}" rx="3" stroke="#333" stroke-width="1"/>
    <text x="{bit_width + (bit_width * exp_bits)//2}" y="{box_height//2 + 5}" text-anchor="middle" fill="white" class="bit">E</text>
    <text x="{bit_width + (bit_width * exp_bits)//2}" y="{box_height + 20}" text-anchor="middle" class="label">{exp_bits}</text>

    <!-- Mantissa bits -->
    <rect x="{bit_width + bit_width * exp_bits}" y="0" width="{bit_width * mant_bits}" height="{box_height}" fill="{mant_color}" rx="3" stroke="#333" stroke-width="1"/>
    <text x="{bit_width + bit_width * exp_bits + (bit_width * mant_bits)//2}" y="{box_height//2 + 5}" text-anchor="middle" fill="white" class="bit">M</text>
    <text x="{bit_width + bit_width * exp_bits + (bit_width * mant_bits)//2}" y="{box_height + 20}" text-anchor="middle" class="label">{mant_bits}</text>
  </g>

  <!-- Extra label if provided -->
  {extra_label_svg}
</svg>'''

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Created: {filepath}")

# FP16: 1 sign, 5 exp, 10 mant
create_svg_file('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/fp16.svg', 1100, 200, "FP16: Half-Precision (16-bit)", 1, 5, 10, "")

# FP32: 1 sign, 8 exp, 23 mant
create_svg_file('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/fp32.svg', 800, 200, "FP32: Single-Precision (32-bit)", 1, 8, 23, "")

# FP64: 1 sign, 11 exp, 52 mant
create_svg_file('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/fp64.svg', 1100, 200, "FP64: Double-Precision (64-bit)", 1, 11, 52, "")

# BF16: 1 sign, 8 exp, 7 mant
create_svg_file('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/bf16.svg', 1100, 200, "BF16: Brain Floating-Point (16-bit)", 1, 8, 7, "")

# HF32: 1 sign, 8 exp, 10 mant
create_svg_file('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/hf32.svg', 1100, 200, "HF32: Brain Floating-Point 32 Compatible", 1, 8, 10, "")

# TF32: 1 sign, 8 exp, 10 mant
create_svg_file('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/tf32.svg', 1100, 200, "TF32: TensorFloat-32", 1, 8, 10, "")

print("Done with FP format SVGs!")
