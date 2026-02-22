#!/usr/bin/env node
/**
 * WaveDrom-style Bitfield SVG Generator for LinxISA
 * 
 * Generates elegant, light-colored SVG bitfield diagrams for instruction encodings.
 * Uses a color palette inspired by WaveDrom's default skin with light, pastel colors.
 * 
 * Usage:
 *   node gen_wavedrom_bitfield.js --spec isa/v0.3/linxisa-v0.3.json --out-dir docs/architecture/isa-manual/src/generated/encodings
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// WaveDrom-inspired light color palette
const COLORS = {
    // Primary field colors (elegant light pastels)
    opcode: '#b9e0ff',      // Light blue
    rd: '#cdfdc5',          // Light green
    rs1: '#ccfdfe',         // Light cyan
    rs2: '#ccfdfe',         // Light cyan
    rs3: '#ccfdfe',         // Light cyan
    imm: '#ffe0b9',         // Light peach/orange
    funct3: '#f0c1fb',      // Light pink/magenta
    funct7: '#f0c1fb',      // Light pink/magenta
    funct12: '#f0c1fb',     // Light pink/magenta
    csr: '#f5c2c0',         // Light coral/red
    
    // Secondary colors
    reserved: '#f5f5f5',    // Very light gray
    empty: '#fafafa',       // Almost white
    default: '#e8e8e8',     // Light gray
    
    // Text and borders
    text: '#333333',
    border: '#666666',
    bitLabel: '#888888'
};

// Simplified color palette for different field types
const FIELD_COLORS = [
    '#b9e0ff', // Light blue - opcode
    '#cdfdc5', // Light green - rd
    '#ffe0b9', // Light peach - immediate
    '#f0c1fb', // Light pink - funct
    '#ccfdfe', // Light cyan - rs1/rs2
    '#f5c2c0', // Light coral - csr
    '#e8e8e8', // Light gray - default
];

/**
 * Parse command line arguments
 */
function parseArgs() {
    const args = process.argv.slice(2);
    let specPath = null;
    let outDir = null;
    let formatSummary = null;
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--spec' && i + 1 < args.length) {
            specPath = args[i + 1];
            i++;
        } else if (args[i] === '--out-dir' && i + 1 < args.length) {
            outDir = args[i + 1];
            i++;
        } else if (args[i] === '--format-summary' && i + 1 < args.length) {
            formatSummary = args[i + 1];
            i++;
        }
    }
    
    if (!specPath || !outDir) {
        console.error('Usage: node gen_wavedrom_bitfield.js --spec <path> --out-dir <path> [--format-summary <path>]');
        process.exit(1);
    }
    
    return { specPath, outDir, formatSummary };
}

/**
 * Get color for a field based on its name
 */
function getFieldColor(fieldName) {
    const name = fieldName.toLowerCase();
    
    if (name.includes('opcode') || name === 'op') return COLORS.opcode;
    if (name === 'rd' || name === 'regdst' || name.includes('dest')) return COLORS.rd;
    if (name === 'rs1' || name === 'srcl' || name === 'src1') return COLORS.rs1;
    if (name === 'rs2' || name === 'srcr' || name === 'src2') return COLORS.rs2;
    if (name === 'rs3' || name === 'srcd' || name === 'src3') return COLORS.rs3;
    if (name.includes('imm') || name.startsWith('uimm') || name.startsWith('simm')) return COLORS.imm;
    if (name.startsWith('funct')) return COLORS.funct3;
    if (name.includes('csr')) return COLORS.csr;
    
    return COLORS.default;
}

/**
 * Generate SVG for a single instruction encoding
 * Different formats for 16-bit, 32-bit, 48-bit, and 64-bit instructions
 */
function generateSVG(mnemonic, length, fields, width = 800, height = 100) {
    const bits = length;
    
    // Adjust dimensions based on instruction length
    let marginLeft, marginRight, marginTop, marginBottom;
    let fieldWidth, rowHeight, fieldHeight, fieldY;
    
    switch (bits) {
        case 16:
            // 16-bit: Compact format
            width = 500;
            height = 80;
            marginLeft = 60;
            marginRight = 15;
            marginTop = 20;
            marginBottom = 25;
            fieldWidth = (width - marginLeft - marginRight) / bits;
            rowHeight = height - marginTop - marginBottom;
            fieldHeight = rowHeight * 0.75;
            fieldY = marginTop + (rowHeight - fieldHeight) / 2;
            break;
        case 32:
            // 32-bit: Standard format
            width = 800;
            height = 100;
            marginLeft = 80;
            marginRight = 20;
            marginTop = 25;
            marginBottom = 35;
            fieldWidth = (width - marginLeft - marginRight) / bits;
            rowHeight = height - marginTop - marginBottom;
            fieldHeight = rowHeight * 0.8;
            fieldY = marginTop + (rowHeight - fieldHeight) / 2;
            break;
        case 48:
            // 48-bit: Prefix + Main format (wider)
            width = 1000;
            height = 120;
            marginLeft = 100;
            marginRight = 25;
            marginTop = 30;
            marginBottom = 40;
            fieldWidth = (width - marginLeft - marginRight) / bits;
            rowHeight = height - marginTop - marginBottom;
            fieldHeight = rowHeight * 0.75;
            fieldY = marginTop + (rowHeight - fieldHeight) / 2;
            break;
        case 64:
            // 64-bit: Prefix + Main format (widest, two rows)
            width = 1000;
            height = 140;
            marginLeft = 100;
            marginRight = 25;
            marginTop = 30;
            marginBottom = 45;
            fieldWidth = (width - marginLeft - marginRight) / 32; // Per 32-bit part
            rowHeight = (height - marginTop - marginBottom) / 2;
            fieldHeight = rowHeight * 0.7;
            fieldY = marginTop + (rowHeight - fieldHeight) / 2;
            break;
        default:
            // Default to 32-bit settings
            width = 800;
            height = 100;
            marginLeft = 80;
            marginRight = 20;
            marginTop = 25;
            marginBottom = 35;
            fieldWidth = (width - marginLeft - marginRight) / bits;
            rowHeight = height - marginTop - marginBottom;
            fieldHeight = rowHeight * 0.8;
            fieldY = marginTop + (rowHeight - fieldHeight) / 2;
    }
    
    // Sort fields by start bit (MSB first)
    const sortedFields = [...fields].sort((a, b) => b.start - a.start);
    
    let svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}">
  <defs>
    <style>
      .field-label { 
        font-family: 'Courier New', monospace; 
        font-size: ${bits === 16 ? '9' : '11'}px; 
        fill: ${COLORS.text};
        font-weight: 500;
      }
      .bit-label { 
        font-family: 'Courier New', monospace; 
        font-size: ${bits === 16 ? '7' : '9'}px; 
        fill: ${COLORS.bitLabel};
        text-anchor: middle; 
      }
      .mnemonic { 
        font-family: 'Helvetica Neue', Arial, sans-serif; 
        font-size: ${bits === 16 ? '12' : '14'}px; 
        font-weight: 600; 
        fill: ${COLORS.text};
      }
      .field-rect { 
        stroke: #ffffff; 
        stroke-width: 1.5px; 
      }
      .border-line {
        stroke: ${COLORS.border};
        stroke-width: 1.5px;
      }
      .part-label {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 10px;
        fill: ${COLORS.bitLabel};
        font-weight: 500;
      }
    </style>
  </defs>
  
  <!-- Mnemonic label -->
  <text x="10" y="18" class="mnemonic">${mnemonic}</text>
  <text x="10" y="${height - 6}" class="bit-label" fill="${COLORS.bitLabel}">${bits}-bit</text>
`;
    
    if (bits === 64) {
        // For 64-bit: show two rows (Part 1: bits 63-32, Part 2: bits 31-0)
        svg += `  <!-- Part 1: bits 63-32 -->
  <text x="${marginLeft - 5}" y="${marginTop + rowHeight / 2 + 4}" class="part-label" text-anchor="end">63-32</text>
  
  <!-- Bit position labels for Part 1 (every 4 bits) -->
`;
        for (let i = 0; i < 32; i += 4) {
            const x = marginLeft + (i + 0.5) * fieldWidth;
            svg += `  <text x="${x}" y="${marginTop - 6}" class="bit-label">${63 - i}</text>\n`;
        }
        
        // Part 1 fields
        const part1Fields = sortedFields.filter(f => f.start >= 32);
        for (const field of part1Fields) {
            const leftPos = 63 - field.start;
            const rightPos = 63 - field.end;
            
            const xLeft = marginLeft + leftPos * fieldWidth;
            const xRight = marginLeft + (rightPos + 1) * fieldWidth;
            const fieldW = xRight - xLeft;
            
            const color = getFieldColor(field.name);
            
            svg += `  <rect x="${xLeft}" y="${fieldY}" width="${fieldW}" height="${fieldHeight}" fill="${color}" class="field-rect" rx="2" ry="2"/>\n`;
            
            if (fieldW > 20) {
                const labelX = xLeft + fieldW / 2;
                const labelY = fieldY + fieldHeight / 2 + 3;
                svg += `  <text x="${labelX}" y="${labelY}" class="field-label" text-anchor="middle">${field.name}</text>\n`;
            }
        }
        
        // Border for Part 1
        svg += `  <line x1="${marginLeft}" y1="${marginTop}" x2="${marginLeft + 32 * fieldWidth}" y2="${marginTop}" class="border-line"/>
  <line x1="${marginLeft}" y1="${marginTop + rowHeight}" x2="${marginLeft + 32 * fieldWidth}" y2="${marginTop + rowHeight}" class="border-line"/>
  
  <!-- Part 2: bits 31-0 -->
  <text x="${marginLeft - 5}" y="${marginTop + rowHeight + rowHeight / 2 + 4}" class="part-label" text-anchor="end">31-0</text>
  
  <!-- Bit position labels for Part 2 -->
`;
        const part2Top = marginTop + rowHeight;
        for (let i = 0; i < 32; i += 4) {
            const x = marginLeft + (i + 0.5) * fieldWidth;
            svg += `  <text x="${x}" y="${part2Top - 6}" class="bit-label">${31 - i}</text>\n`;
        }
        
        // Part 2 fields
        const part2Fields = sortedFields.filter(f => f.start < 32);
        const part2Y = part2Top + (rowHeight - fieldHeight) / 2;
        for (const field of part2Fields) {
            const leftPos = 31 - field.start;
            const rightPos = 31 - field.end;
            
            const xLeft = marginLeft + leftPos * fieldWidth;
            const xRight = marginLeft + (rightPos + 1) * fieldWidth;
            const fieldW = xRight - xLeft;
            
            const color = getFieldColor(field.name);
            
            svg += `  <rect x="${xLeft}" y="${part2Y}" width="${fieldW}" height="${fieldHeight}" fill="${color}" class="field-rect" rx="2" ry="2"/>\n`;
            
            if (fieldW > 20) {
                const labelX = xLeft + fieldW / 2;
                const labelY = part2Y + fieldHeight / 2 + 3;
                svg += `  <text x="${labelX}" y="${labelY}" class="field-label" text-anchor="middle">${field.name}</text>\n`;
            }
        }
        
        // Border for Part 2
        svg += `  <line x1="${marginLeft}" y1="${part2Top}" x2="${marginLeft + 32 * fieldWidth}" y2="${part2Top}" class="border-line"/>
  <line x1="${marginLeft}" y1="${part2Top + rowHeight}" x2="${marginLeft + 32 * fieldWidth}" y2="${part2Top + rowHeight}" class="border-line"/>
</svg>`;
        
        return svg;
    }
    
    // For 16-bit, 32-bit, 48-bit: single row format
    // Bit position labels (show every 4 bits for 32-bit, every 2 bits for 16-bit)
    const bitStep = bits <= 16 ? 2 : 4;
    for (let i = 0; i < bits; i += bitStep) {
        const x = marginLeft + (i + 0.5) * fieldWidth;
        svg += `  <text x="${x}" y="${marginTop - 6}" class="bit-label">${bits - 1 - i}</text>\n`;
    }
    
    // Add field rectangles
    for (const field of sortedFields) {
        const leftPos = bits - 1 - field.start;
        const rightPos = bits - 1 - field.end;
        
        const xLeft = marginLeft + leftPos * fieldWidth;
        const xRight = marginLeft + (rightPos + 1) * fieldWidth;
        const fieldW = xRight - xLeft;
        
        const color = getFieldColor(field.name);
        
        const rx = bits === 16 ? 2 : 3;
        svg += `  <rect x="${xLeft}" y="${fieldY}" width="${fieldW}" height="${fieldHeight}" fill="${color}" class="field-rect" rx="${rx}" ry="${rx}"/>\n`;
        
        // Add field label if there's enough space
        const minWidth = bits === 16 ? 15 : 25;
        if (fieldW > minWidth) {
            const labelX = xLeft + fieldW / 2;
            const labelY = fieldY + fieldHeight / 2 + (bits === 16 ? 2 : 4);
            svg += `  <text x="${labelX}" y="${labelY}" class="field-label" text-anchor="middle">${field.name}</text>\n`;
        }
    }
    
    // Add border lines
    svg += `  
  <!-- Border lines -->
  <line x1="${marginLeft}" y1="${marginTop}" x2="${marginLeft + bits * fieldWidth}" y2="${marginTop}" class="border-line"/>
  <line x1="${marginLeft}" y1="${marginTop + rowHeight}" x2="${marginLeft + bits * fieldWidth}" y2="${marginTop + rowHeight}" class="border-line"/>
</svg>`;
    
    return svg;
}

/**
 * Parse instruction fields from JSON spec
 * The JSON uses 'msb' and 'lsb' directly in segments, and 'token' for field names
 */
function parseFields(inst, partIndex = 0) {
    const fields = [];
    
    const parts = inst.parts || [];
    if (partIndex >= parts.length) return fields;
    
    const part = parts[partIndex];
    const segments = part.segments || [];
    
    for (const seg of segments) {
        // Use token as field name, or fallback to name
        const fieldName = seg.token || seg.name || 'unknown';
        
        // Skip constant-only fields (they have 'const' property but no lsb/msb in our case)
        // Actually, constants still have lsb/msb but with const property
        let msb = seg.msb;
        let lsb = seg.lsb;
        
        // If not directly available, check bit_range
        if (msb === undefined && lsb === undefined) {
            const bitRange = seg.bit_range || {};
            msb = bitRange.msb;
            lsb = bitRange.lsb;
        }
        
        if (msb === undefined || lsb === undefined) continue;
        
        fields.push({
            name: fieldName,
            start: msb,
            end: lsb,
            isConst: seg.const !== undefined,
            constValue: seg.const?.value
        });
    }
    
    return fields;
}

/**
 * Generate encoding diagrams for all instructions
 */
function generateEncodings(specPath, outputDir) {
    console.log(`Reading specification from: ${specPath}`);
    
    const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
    const instructions = spec.instructions || [];
    
    console.log(`Found ${instructions.length} instructions`);
    
    // Create output directory
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    let count = 0;
    
    for (const inst of instructions) {
        const mnemonic = inst.mnemonic || 'UNKNOWN';
        
        // Get instruction length - check multiple possible fields
        let length = inst.length_bits || inst.length || 32;
        
        const parts = inst.parts || [];
        if (!parts.length) continue;
        
        for (let partIdx = 0; partIdx < parts.length; partIdx++) {
            const part = parts[partIdx];
            // Each part has its own length
            const partLength = part.length || part.width_bits || length;
            
            const fields = parseFields(inst, partIdx);
            
            // Create safe filename
            let safeName = mnemonic.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
            if (parts.length > 1) {
                safeName += `_part${partIdx + 1}`;
            }
            
            // Use total instruction length for SVG rendering
            // (64-bit instructions have two 32-bit parts but should render as 64-bit)
            const svg = generateSVG(mnemonic, length, fields);
            
            const svgPath = path.join(outputDir, `enc_${safeName}.svg`);
            fs.writeFileSync(svgPath, svg);
            
            count++;
        }
    }
    
    console.log(`Generated ${count} SVG encoding diagrams in ${outputDir}`);
    return count;
}

/**
 * Generate format summary
 */
function generateFormatSummary(specPath, outputPath) {
    const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
    
    const formats = {};
    
    for (const inst of spec.instructions || []) {
        for (let partIdx = 0; partIdx < (inst.parts || []).length; partIdx++) {
            const part = inst.parts[partIdx];
            const decode = part.decode || 'Unknown';
            
            if (!formats[decode]) {
                formats[decode] = {
                    count: 0,
                    length: part.length || 32,
                    fields: new Set()
                };
            }
            
            formats[decode].count++;
            
            for (const seg of part.segments || []) {
                formats[decode].fields.add(seg.name || 'unknown');
            }
        }
    }
    
    // Generate AsciiDoc
    const lines = [
        '// Generated file; do not edit by hand.',
        '',
        '[[encoding-format-summary]]',
        '=== Instruction Format Summary',
        '',
        '[cols="1,1,1,3",options="header"]',
        '|===',
        '|Format |Bits |Count |Fields'
    ];
    
    for (const [fmt, info] of Object.entries(formats).sort()) {
        const fieldsArray = Array.from(info.fields);
        const fieldsStr = fieldsArray.slice(0, 6).join(', ');
        const extra = fieldsArray.length > 6 ? ` ... (${fieldsArray.length} total)` : '';
        lines.push(`|\`${fmt}\` |${info.length} |${info.count} |${fieldsStr}${extra}`);
    }
    
    lines.push('|===');
    
    // Write file
    const dir = path.dirname(outputPath);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
    
    fs.writeFileSync(outputPath, lines.join('\n'));
    console.log(`Generated format summary at ${outputPath}`);
    
    return Object.keys(formats).length;
}

/**
 * Main entry point
 */
function main() {
    const { specPath, outDir, formatSummary } = parseArgs();
    
    // Generate encoding diagrams
    const count = generateEncodings(specPath, outDir);
    
    // Generate format summary if requested
    if (formatSummary) {
        generateFormatSummary(specPath, formatSummary);
    }
    
    process.exit(count > 0 ? 0 : 1);
}

main();
