# LDA

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** LDA &nbsp;|&nbsp;
**Forms:** 11 &nbsp;|&nbsp;
**Unique mnemonics:** 11

</div>

Instructions in the **LDA** group of the LinxISA v0.58.5 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.PRF](../instructions/hl_prf.md) | `hl.prf{.l1,.l2,.l3} [SrcL, SrcR<{.sw,.uw}><<<shamt>]` | 48 | — | HL.PRF snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint with no destination effect. |
| [HL.PRF.A](../instructions/hl_prf_a.md) | `hl.prf.a{.l1,.l2,.l3} [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->{t, u, Rd}` | 48 | — | HL.PRF.A snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint and publishes the effective address. |
| [HL.PRFI.U](../instructions/hl_prfi_u.md) | `hl.prfi.u{.l1,.l2,.l3} [SrcL, simm]` | 48 | — | HL.PRFI.U snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint with no destination effect. |
| [HL.PRFI.UA](../instructions/hl_prfi_ua.md) | `hl.prfi.ua{.l1,.l2,.l3} [SrcL, simm], ->{t, u, Rd}` | 48 | — | HL.PRFI.UA snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint and publishes the effective address. |
| [LB.PCR](../instructions/lb_pcr.md) | `lb.pcr [symbol], ->{t, u, Rd}` | 32 | — | LB.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [LBU.PCR](../instructions/lbu_pcr.md) | `lbu.pcr [symbol], ->{t, u, Rd}` | 32 | — | LBU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [LD.PCR](../instructions/ld_pcr.md) | `ld.pcr [symbol], ->{t, u, Rd}` | 32 | — | LD.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [LH.PCR](../instructions/lh_pcr.md) | `lh.pcr [symbol], ->{t, u, Rd}` | 32 | — | LH.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LHU.PCR](../instructions/lhu_pcr.md) | `lhu.pcr [symbol], ->{t, u, Rd}` | 32 | — | LHU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LW.PCR](../instructions/lw_pcr.md) | `lw.pcr [symbol], ->{t, u, Rd}` | 32 | — | LW.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [LWU.PCR](../instructions/lwu_pcr.md) | `lwu.pcr [symbol], ->{t, u, Rd}` | 32 | — | LWU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
