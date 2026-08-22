# STA/PC_REL

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** STA/PC_REL &nbsp;|&nbsp;
**Forms:** 4 &nbsp;|&nbsp;
**Unique mnemonics:** 4

</div>

Instructions in the **STA/PC_REL** group of the LinxISA v0.58.3 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.SB.PCR](../instructions/hl_sb_pcr.md) | `hl.sb.pcr SrcL, [<symbol>]` | 48 | — | HL.SB.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [HL.SD.PCR](../instructions/hl_sd_pcr.md) | `hl.sd.pcr SrcL, [<symbol>]` | 48 | — | HL.SD.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SH.PCR](../instructions/hl_sh_pcr.md) | `hl.sh.pcr SrcL, [<symbol>]` | 48 | — | HL.SH.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SW.PCR](../instructions/hl_sw_pcr.md) | `hl.sw.pcr SrcL, [<symbol>]` | 48 | — | HL.SW.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
