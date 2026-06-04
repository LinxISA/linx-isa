#!/usr/bin/env python3
"""Generate FP8/FP6/FP4 format SVG diagrams"""

def create_fp8_svg(filepath, width, height, title, exp_bits, mant_bits, extra_label=""):
    """Create a floating-point format SVG diagram for small formats"""
    # Colors
    sign_color = "#808080"  # Gray
    exp_color = "#4169E1"   # Royal Blue
    mant_color = "#228B22"  # Forest Green

    # Calculate dimensions
    box_height = 80
    bit_width = 24
    total_bits = 1 + exp_bits + mant_bits

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
  <text x="10" y="50" class="label">{total_bits-1}</text>
  <text x="{width-20}" y="50" class="label">0</text>

  <!-- Main bit boxes -->
  <g transform="translate({(width - (bit_width * total_bits))//2}, 60)">
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

# E4M3: 1 sign, 4 exp, 3 mant (FP8)
create_fp8_svg('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/e4m3.svg', 800, 200, "FP8 E4M3: E4M3 Format", 4, 3, "No Inf, NaN=1111")

# E5M2: 1 sign, 5 exp, 2 mant (FP8)
create_fp8_svg('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/e5m2.svg', 800, 200, "FP8 E5M2: E5M2 Format", 5, 2, "Inf, NaN supported")

# E3M2: 1 sign, 3 exp, 2 mant (FP6)
create_fp8_svg('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/e3m2.svg', 800, 200, "FP6 E3M2: E3M2 Format", 3, 2, "")

# E2M3: 1 sign, 2 exp, 3 mant (FP6)
create_fp8_svg('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/e2m3.svg', 800, 200, "FP6 E2M3: E2M3 Format", 2, 3, "")

# E2M1: 1 sign, 2 exp, 1 mant (FP4)
create_fp8_svg('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/e2m1.svg', 800, 200, "FP4 E2M1: E2M1 Format", 2, 1, "")

# E1M2: 1 sign, 1 exp, 2 mant (FP4)
create_fp8_svg('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/e1m2.svg', 800, 200, "FP4 E1M2: E1M2 Format", 1, 2, "")

# E6M2: 1 sign, 6 exp, 2 mant (scaling format)
create_fp8_svg('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/e6m2.svg', 400, 200, "E6M2: Scaling Format", 6, 2, "")

# E8M0: MX_SCALE 8-bit mantissa
svg_e8m0 = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="200" viewBox="0 0 600 200">
  <style>
    text { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 14px; }
    .title { font-size: 18px; font-weight: bold; fill: #333; }
    .label { font-size: 12px; fill: #555; }
  </style>

  <text x="10" y="25" class="title">MX_SCALE E8M0: 8-bit Mantissa with Shared Exponent</text>

  <g transform="translate(50, 60)">
    <!-- Mantissa box (8 bits) -->
    <rect x="0" y="0" width="192" height="80" fill="#228B22" rx="3" stroke="#333" stroke-width="1"/>
    <text x="96" y="45" text-anchor="middle" fill="white">M (8 bits)</text>
    <text x="96" y="110" text-anchor="middle" class="label">8-bit mantissa</text>

    <!-- Shared exponent indicator -->
    <rect x="210" y="0" width="80" height="80" fill="#9370DB" rx="3" stroke="#333" stroke-width="1" stroke-dasharray="5,3"/>
    <text x="250" y="45" text-anchor="middle" fill="#333">Shared</text>
    <text x="250" y="65" text-anchor="middle" fill="#333">Exp</text>
    <text x="250" y="110" text-anchor="middle" class="label">shared across group</text>
  </g>
</svg>'''

with open('/Users/zhoubot/linx-isa/docs/figs/isa/datatype/E8M0.svg', 'w', encoding='utf-8') as f:
    f.write(svg_e8m0)
print("Created: /Users/zhoubot/linx-isa/docs/figs/isa/datatype/E8M0.svg")

print("Done with FP8/FP6/FP4 format SVGs!")
