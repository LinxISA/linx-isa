# LDA/UNSCALED

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** LDA/UNSCALED &nbsp;|&nbsp;
**Forms:** 6 &nbsp;|&nbsp;
**Unique mnemonics:** 6

</div>

Instructions in the **LDA/UNSCALED** group of the LinxISA v0.58.5 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [LDI.U](../instructions/ldi_u.md) | `ldi.u [SrcL, simm], ->{t, u, Rd}` | 32 | — | LDI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [LHI.U](../instructions/lhi_u.md) | `lhi.u [SrcL, simm], ->{t, u, Rd}` | 32 | — | LHI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LHUI.U](../instructions/lhui_u.md) | `lhui.u [SrcL, simm], ->{t, u, Rd}` | 32 | — | LHUI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LWI.U](../instructions/lwi_u.md) | `lwi.u [SrcL, simm], ->{t, u, Rd}` | 32 | — | LWI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [LWUI.U](../instructions/lwui_u.md) | `lwui.u [SrcL, simm], ->{t, u, Rd}` | 32 | — | LWUI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [PRFI.U](../instructions/prfi_u.md) | `prfi.u [SrcL, simm]` | 32 | — | PRFI.U snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint with no destination effect. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
