# LDA/BASE_IMM

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** LDA/BASE_IMM &nbsp;|&nbsp;
**Forms:** 9 &nbsp;|&nbsp;
**Unique mnemonics:** 9

</div>

Instructions in the **LDA/BASE_IMM** group of the LinxISA v0.58.1 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [C.LDI](../instructions/c_ldi.md) | `c.ldi [srcL, simm], ->t` | 16 | — | C.LDI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [C.LWI](../instructions/c_lwi.md) | `c.lwi [srcL, simm], ->t` | 16 | — | C.LWI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [LBI](../instructions/lbi.md) | `lbi [SrcL, simm], ->{t, u, Rd}` | 32 | — | LBI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [LBUI](../instructions/lbui.md) | `lbui [SrcL, simm], ->{t, u, Rd}` | 32 | — | LBUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [LDI](../instructions/ldi.md) | `ldi [SrcL, simm], ->{t, u, Rd}` | 32 | — | LDI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [LHI](../instructions/lhi.md) | `lhi [SrcL, simm], ->{t, u, Rd}` | 32 | — | LHI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LHUI](../instructions/lhui.md) | `lhui [SrcL, simm], ->{t, u, Rd}` | 32 | — | LHUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LWI](../instructions/lwi.md) | `lwi [SrcL, simm], ->{t, u, Rd}` | 32 | — | LWI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [LWUI](../instructions/lwui.md) | `lwui [SrcL, simm], ->{t, u, Rd}` | 32 | — | LWUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
