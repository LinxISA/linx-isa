#!/usr/bin/env python3
"""Generate instruction encoding space SVG diagrams"""

# encodingspace.svg - Overview of all four formats
svg_encodingspace = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="300" viewBox="0 0 900 300">
  <style>
    text { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 14px; }
    .title { font-size: 20px; font-weight: bold; fill: #333; }
    .label { font-size: 12px; fill: #555; }
    .format-label { font-size: 14px; font-weight: bold; fill: white; }
    .bits-label { font-size: 11px; fill: #333; }
  </style>

  <text x="10" y="25" class="title">LinxISA v0.57 Instruction Encoding Space</text>

  <!-- Row of format boxes -->
  <g transform="translate(50, 50)">
    <!-- C16: 16-bit -->
    <rect x="0" y="0" width="150" height="180" fill="#FF6B6B" rx="5" stroke="#333" stroke-width="2"/>
    <text x="75" y="30" text-anchor="middle" class="format-label">C16</text>
    <text x="75" y="55" text-anchor="middle" class="label" fill="white">16-bit</text>
    <text x="75" y="100" text-anchor="middle" class="bits-label">[15:0]</text>
    <text x="75" y="140" text-anchor="middle" class="label">Compressed</text>
    <text x="75" y="160" text-anchor="middle" class="label">Format</text>

    <!-- LX32: 32-bit -->
    <rect x="170" y="0" width="180" height="180" fill="#4ECDC4" rx="5" stroke="#333" stroke-width="2"/>
    <text x="260" y="30" text-anchor="middle" class="format-label">LX32</text>
    <text x="260" y="55" text-anchor="middle" class="label" fill="white">32-bit</text>
    <text x="260" y="100" text-anchor="middle" class="bits-label">[31:0]</text>
    <text x="260" y="140" text-anchor="middle" class="label">Standard</text>
    <text x="260" y="160" text-anchor="middle" class="label">Format</text>

    <!-- HL48: 48-bit with prefix -->
    <rect x="370" y="0" width="220" height="180" fill="#45B7D1" rx="5" stroke="#333" stroke-width="2"/>
    <text x="480" y="30" text-anchor="middle" class="format-label">HL48</text>
    <text x="480" y="55" text-anchor="middle" class="label" fill="white">48-bit</text>
    <text x="430" y="100" text-anchor="middle" class="bits-label">[47:32]</text>
    <text x="530" y="100" text-anchor="middle" class="bits-label">[31:0]</text>
    <text x="430" y="130" text-anchor="middle" class="label">16-bit</text>
    <text x="530" y="130" text-anchor="middle" class="label">32-bit</text>
    <text x="430" y="145" text-anchor="middle" class="label">prefix</text>
    <text x="530" y="145" text-anchor="middle" class="label">main</text>
    <text x="480" y="170" text-anchor="middle" class="label">Half-Load</text>

    <!-- V64: 64-bit with prefix -->
    <rect x="610" y="0" width="250" height="180" fill="#96CEB4" rx="5" stroke="#333" stroke-width="2"/>
    <text x="735" y="30" text-anchor="middle" class="format-label">V64</text>
    <text x="735" y="55" text-anchor="middle" class="label" fill="white">64-bit</text>
    <text x="660" y="100" text-anchor="middle" class="bits-label">[63:32]</text>
    <text x="810" y="100" text-anchor="middle" class="bits-label">[31:0]</text>
    <text x="660" y="130" text-anchor="middle" class="label">32-bit</text>
    <text x="810" y="130" text-anchor="middle" class="label">32-bit</text>
    <text x="660" y="145" text-anchor="middle" class="label">prefix</text>
    <text x="810" y="145" text-anchor="middle" class="label">main</text>
    <text x="735" y="170" text-anchor="middle" class="label">Vector</text>
  </g>

  <!-- Legend at bottom -->
  <g transform="translate(50, 260)">
    <rect x="0" y="0" width="20" height="20" fill="#FF6B6B" rx="2"/>
    <text x="30" y="15" class="label">Compressed (16-bit)</text>

    <rect x="180" y="0" width="20" height="20" fill="#4ECDC4" rx="2"/>
    <text x="210" y="15" class="label">Standard (32-bit)</text>

    <rect x="350" y="0" width="20" height="20" fill="#45B7D1" rx="2"/>
    <text x="380" y="15" class="label">Half-Load (48-bit)</text>

    <rect x="530" y="0" width="20" height="20" fill="#96CEB4" rx="2"/>
    <text x="560" y="15" class="label">Vector (64-bit)</text>
  </g>
</svg>'''

with open('/Users/zhoubot/linx-isa/docs/figs/isa/space/encodingspace.svg', 'w', encoding='utf-8') as f:
    f.write(svg_encodingspace)
print("Created: encodingspace.svg")

# space-16bit.svg - C16 Encoding Space
svg_space_16bit = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="300" viewBox="0 0 900 300">
  <style>
    text { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 14px; }
    .title { font-size: 18px; font-weight: bold; fill: #333; }
    .label { font-size: 12px; fill: #555; }
    .bit-label { font-size: 11px; fill: #333; }
  </style>

  <text x="10" y="25" class="title">C16 Encoding Space (16-bit)</text>
  <text x="10" y="45" class="label">3 major opcode bits [15:13] divide space into 8 slots</text>

  <!-- Bit positions at top -->
  <g transform="translate(50, 60)">
    <text x="0" y="0" class="bit-label">15</text>
    <text x="135" y="0" class="bit-label">13</text>
    <text x="180" y="0" class="bit-label">12</text>
    <text x="345" y="0" class="bit-label">0</text>

    <!-- Opcode field highlight -->
    <rect x="0" y="10" width="150" height="60" fill="#FFE4B5" rx="3" stroke="#333" stroke-width="1" stroke-dasharray="5,3"/>
    <text x="75" y="45" text-anchor="middle" class="label" font-weight="bold">opcode</text>
    <text x="75" y="60" text-anchor="middle" class="bit-label">[15:13]</text>

    <!-- Remaining bits -->
    <rect x="150" y="10" width="180" height="60" fill="#E8E8E8" rx="3" stroke="#333" stroke-width="1"/>
    <text x="240" y="45" text-anchor="middle" class="label">operands/imm</text>
    <text x="240" y="60" text-anchor="middle" class="bit-label">[12:0]</text>
  </g>

  <!-- 8 opcode slots -->
  <g transform="translate(50, 100)">
    <text x="0" y="15" class="label" font-weight="bold">Opcode Slots:</text>

    <rect x="0" y="25" width="100" height="60" fill="#FF6B6B" rx="3" stroke="#333" stroke-width="1"/>
    <text x="50" y="55" text-anchor="middle" class="label" fill="white">000</text>
    <text x="50" y="100" text-anchor="middle" class="bit-label">Slot 0</text>

    <rect x="110" y="25" width="100" height="60" fill="#FF6B6B" rx="3" stroke="#333" stroke-width="1"/>
    <text x="160" y="55" text-anchor="middle" class="label" fill="white">001</text>
    <text x="160" y="100" text-anchor="middle" class="bit-label">Slot 1</text>

    <rect x="220" y="25" width="100" height="60" fill="#FF6B6B" rx="3" stroke="#333" stroke-width="1"/>
    <text x="270" y="55" text-anchor="middle" class="label" fill="white">010</text>
    <text x="270" y="100" text-anchor="middle" class="bit-label">Slot 2</text>

    <rect x="330" y="25" width="100" height="60" fill="#FF6B6B" rx="3" stroke="#333" stroke-width="1"/>
    <text x="380" y="55" text-anchor="middle" class="label" fill="white">011</text>
    <text x="380" y="100" text-anchor="middle" class="bit-label">Slot 3</text>

    <rect x="440" y="25" width="100" height="60" fill="#FF6B6B" rx="3" stroke="#333" stroke-width="1"/>
    <text x="490" y="55" text-anchor="middle" class="label" fill="white">100</text>
    <text x="490" y="100" text-anchor="middle" class="bit-label">Slot 4</text>

    <rect x="550" y="25" width="100" height="60" fill="#FF6B6B" rx="3" stroke="#333" stroke-width="1"/>
    <text x="600" y="55" text-anchor="middle" class="label" fill="white">101</text>
    <text x="600" y="100" text-anchor="middle" class="bit-label">Slot 5</text>

    <rect x="660" y="25" width="100" height="60" fill="#FF6B6B" rx="3" stroke="#333" stroke-width="1"/>
    <text x="710" y="55" text-anchor="middle" class="label" fill="white">110</text>
    <text x="710" y="100" text-anchor="middle" class="bit-label">Slot 6</text>

    <rect x="770" y="25" width="100" height="60" fill="#FF6B6B" rx="3" stroke="#333" stroke-width="1"/>
    <text x="820" y="55" text-anchor="middle" class="label" fill="white">111</text>
    <text x="820" y="100" text-anchor="middle" class="bit-label">Slot 7</text>
  </g>
</svg>'''

with open('/Users/zhoubot/linx-isa/docs/figs/isa/space/space-16bit.svg', 'w', encoding='utf-8') as f:
    f.write(svg_space_16bit)
print("Created: space-16bit.svg")

# space-32bit.svg - LX32 Encoding Space
svg_space_32bit = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="300" viewBox="0 0 900 300">
  <style>
    text { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 14px; }
    .title { font-size: 18px; font-weight: bold; fill: #333; }
    .label { font-size: 12px; fill: #555; }
    .bit-label { font-size: 11px; fill: #333; }
  </style>

  <text x="10" y="25" class="title">LX32 Encoding Space (32-bit)</text>
  <text x="10" y="45" class="label">6 major opcode bits [31:26] divide space into 64 slots</text>

  <!-- Bit positions at top -->
  <g transform="translate(50, 60)">
    <text x="0" y="0" class="bit-label">31</text>
    <text x="90" y="0" class="bit-label">26</text>
    <text x="120" y="0" class="bit-label">25</text>
    <text x="330" y="0" class="bit-label">0</text>

    <!-- Opcode field highlight -->
    <rect x="0" y="10" width="100" height="60" fill="#FFE4B5" rx="3" stroke="#333" stroke-width="1" stroke-dasharray="5,3"/>
    <text x="50" y="45" text-anchor="middle" class="label" font-weight="bold">opcode</text>
    <text x="50" y="60" text-anchor="middle" class="bit-label">[31:26]</text>

    <!-- Remaining bits -->
    <rect x="100" y="10" width="220" height="60" fill="#E8E8E8" rx="3" stroke="#333" stroke-width="1"/>
    <text x="210" y="45" text-anchor="middle" class="label">operands/imm</text>
    <text x="210" y="60" text-anchor="middle" class="bit-label">[25:0]</text>
  </g>

  <!-- 64 opcode slots grid (8x8) -->
  <g transform="translate(50, 100)">
    <text x="0" y="15" class="label" font-weight="bold">64 Opcode Slots (6-bit opcode):</text>

    <!-- Row 1 -->
    <rect x="0" y="25" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="50" y="45" text-anchor="middle" class="label" fill="white" font-size="10">000000</text>

    <rect x="110" y="25" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="160" y="45" text-anchor="middle" class="label" fill="white" font-size="10">000001</text>

    <rect x="220" y="25" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="270" y="45" text-anchor="middle" class="label" fill="white" font-size="10">000010</text>

    <rect x="330" y="25" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="380" y="45" text-anchor="middle" class="label" fill="white" font-size="10">000011</text>

    <rect x="440" y="25" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="490" y="45" text-anchor="middle" class="label" fill="white" font-size="10">000100</text>

    <rect x="550" y="25" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="600" y="45" text-anchor="middle" class="label" fill="white" font-size="10">000101</text>

    <rect x="660" y="25" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="710" y="45" text-anchor="middle" class="label" fill="white" font-size="10">000110</text>

    <rect x="770" y="25" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="820" y="45" text-anchor="middle" class="label" fill="white" font-size="10">000111</text>

    <!-- Row 2 -->
    <rect x="0" y="60" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="50" y="80" text-anchor="middle" class="label" fill="white" font-size="10">001000</text>

    <rect x="110" y="60" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="160" y="80" text-anchor="middle" class="label" fill="white" font-size="10">001001</text>

    <!-- ... more slots ... -->
    <text x="430" y="80" text-anchor="middle" class="bit-label">...</text>

    <rect x="770" y="60" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="820" y="80" text-anchor="middle" class="label" fill="white" font-size="10">001111</text>

    <!-- More rows as dotted area -->
    <rect x="0" y="95" width="870" height="50" fill="#E8E8E8" rx="2" stroke="#999" stroke-width="1" stroke-dasharray="5,3"/>
    <text x="435" y="125" text-anchor="middle" class="label">...</text>

    <!-- Last row -->
    <rect x="0" y="150" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="50" y="170" text-anchor="middle" class="label" fill="white" font-size="10">111000</text>

    <rect x="770" y="150" width="100" height="30" fill="#4ECDC4" rx="2" stroke="#333" stroke-width="1"/>
    <text x="820" y="170" text-anchor="middle" class="label" fill="white" font-size="10">111111</text>
  </g>
</svg>'''

with open('/Users/zhoubot/linx-isa/docs/figs/isa/space/space-32bit.svg', 'w', encoding='utf-8') as f:
    f.write(svg_space_32bit)
print("Created: space-32bit.svg")

print("Done with first 3 encoding space SVGs!")
