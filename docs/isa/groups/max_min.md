# Max-Min

<div class="insn-header">

<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Group:** Max-Min &nbsp;|&nbsp;
**Forms:** 6 &nbsp;|&nbsp;
**Unique mnemonics:** 6

</div>

Integer max/min instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [FMAX](../instructions/fmax.md) | `fmax.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point maximum. |
| [FMIN](../instructions/fmin.md) | `fmin.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point minimum. |
| [MAX](../instructions/max.md) | `max SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Integer max (signed). |
| [MAXU](../instructions/maxu.md) | `maxu SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Instruction from the Max-Min group. |
| [MIN](../instructions/min.md) | `min SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Integer min (signed). |
| [MINU](../instructions/minu.md) | `minu SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Instruction from the Max-Min group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 16: BRU — Branch and Compare](../index.md)
- [Encoding formats](../encoding.md)
