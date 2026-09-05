# LDA/BASE_REG

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** LDA/BASE_REG &nbsp;|&nbsp;
**Forms:** 8 &nbsp;|&nbsp;
**Unique mnemonics:** 8

</div>

Instructions in the **LDA/BASE_REG** group of the LinxISA v0.58.6 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [LB](../instructions/lb.md) | `lb [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->{t, u, Rd}` | 32 | — | LB snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [LBU](../instructions/lbu.md) | `lbu [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->{t, u, Rd}` | 32 | — | LBU snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [LD](../instructions/ld.md) | `ld [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->{t, u, Rd}` | 32 | — | LD snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [LH](../instructions/lh.md) | `lh [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->{t, u, Rd}` | 32 | — | LH snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LHU](../instructions/lhu.md) | `lhu [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->{t, u, Rd}` | 32 | — | LHU snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LW](../instructions/lw.md) | `lw [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->{t, u, Rd}` | 32 | — | LW snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [LWU](../instructions/lwu.md) | `lwu [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->{t, u, Rd}` | 32 | — | LWU snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [PRF](../instructions/prf.md) | `prf [SrcL, SrcR<{.sw,.uw}><<<shamt>]` | 32 | — | PRF snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint with no destination effect. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
