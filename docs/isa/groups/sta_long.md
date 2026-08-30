# STA/LONG

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** STA/LONG &nbsp;|&nbsp;
**Forms:** 7 &nbsp;|&nbsp;
**Unique mnemonics:** 7

</div>

Instructions in the **STA/LONG** group of the LinxISA v0.58.5 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.SBI](../instructions/hl_sbi.md) | `hl.sbi SrcD, [SrcR, simm]` | 48 | — | HL.SBI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [HL.SDI](../instructions/hl_sdi.md) | `hl.sdi SrcD, [SrcR, simm]` | 48 | — | HL.SDI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SDI.U](../instructions/hl_sdi_u.md) | `hl.sdi.u SrcD, [SrcR, simm]` | 48 | — | HL.SDI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SHI](../instructions/hl_shi.md) | `hl.shi SrcD, [SrcR, simm]` | 48 | — | HL.SHI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SHI.U](../instructions/hl_shi_u.md) | `hl.shi.u SrcD, [SrcR, simm]` | 48 | — | HL.SHI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SWI](../instructions/hl_swi.md) | `hl.swi SrcD, [SrcR, simm]` | 48 | — | HL.SWI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SWI.U](../instructions/hl_swi_u.md) | `hl.swi.u SrcD, [SrcR, simm]` | 48 | — | HL.SWI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
