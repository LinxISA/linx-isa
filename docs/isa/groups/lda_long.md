# LDA/LONG

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** LDA/LONG &nbsp;|&nbsp;
**Forms:** 12 &nbsp;|&nbsp;
**Unique mnemonics:** 12

</div>

Instructions in the **LDA/LONG** group of the LinxISA v0.58.3 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.LBI](../instructions/hl_lbi.md) | `hl.lbi [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.LBI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBUI](../instructions/hl_lbui.md) | `hl.lbui [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.LBUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LDI](../instructions/hl_ldi.md) | `hl.ldi [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.LDI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LDI.U](../instructions/hl_ldi_u.md) | `hl.ldi.u [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.LDI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LHI](../instructions/hl_lhi.md) | `hl.lhi [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.LHI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHI.U](../instructions/hl_lhi_u.md) | `hl.lhi.u [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.LHI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHUI](../instructions/hl_lhui.md) | `hl.lhui [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.LHUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHUI.U](../instructions/hl_lhui_u.md) | `hl.lhui.u [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.LHUI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LWI](../instructions/hl_lwi.md) | `hl.lwi [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.LWI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWI.U](../instructions/hl_lwi_u.md) | `hl.lwi.u [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.LWI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWUI](../instructions/hl_lwui.md) | `hl.lwui [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.LWUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWUI.U](../instructions/hl_lwui_u.md) | `hl.lwui.u [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.LWUI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
