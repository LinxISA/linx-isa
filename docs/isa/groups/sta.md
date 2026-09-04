# STA

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** STA &nbsp;|&nbsp;
**Forms:** 4 &nbsp;|&nbsp;
**Unique mnemonics:** 4

</div>

Instructions in the **STA** group of the LinxISA v0.58.5 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [SB.PCR](../instructions/sb_pcr.md) | `sb.pcr SrcL, [symbol]` | 32 | — | SB.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [SD.PCR](../instructions/sd_pcr.md) | `sd.pcr SrcL, [symbol]` | 32 | — | SD.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [SH.PCR](../instructions/sh_pcr.md) | `sh.pcr SrcL, [symbol]` | 32 | — | SH.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [SW.PCR](../instructions/sw_pcr.md) | `sw.pcr SrcL, [symbol]` | 32 | — | SW.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
