# LDA/PC_REL

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** LDA/PC_REL &nbsp;|&nbsp;
**Forms:** 7 &nbsp;|&nbsp;
**Unique mnemonics:** 7

</div>

Instructions in the **LDA/PC_REL** group of the LinxISA v0.58.6 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.LB.PCR](../instructions/hl_lb_pcr.md) | `hl.lb.pcr [<symbol>], ->{t, u, Rd}` | 48 | — | HL.LB.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBU.PCR](../instructions/hl_lbu_pcr.md) | `hl.lbu.pcr [<symbol>], ->{t, u, Rd}` | 48 | — | HL.LBU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LD.PCR](../instructions/hl_ld_pcr.md) | `hl.ld.pcr [<symbol>], ->{t, u, Rd}` | 48 | — | HL.LD.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LH.PCR](../instructions/hl_lh_pcr.md) | `hl.lh.pcr [<symbol>], ->{t, u, Rd}` | 48 | — | HL.LH.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHU.PCR](../instructions/hl_lhu_pcr.md) | `hl.lhu.pcr [<symbol>], ->{t, u, Rd}` | 48 | — | HL.LHU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LW.PCR](../instructions/hl_lw_pcr.md) | `hl.lw.pcr [<symbol>], ->{t, u, Rd}` | 48 | — | HL.LW.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWU.PCR](../instructions/hl_lwu_pcr.md) | `hl.lwu.pcr [<symbol>], ->{t, u, Rd}` | 48 | — | HL.LWU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
