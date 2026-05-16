# Bit Operation

<div class="insn-header">

<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Group:** Bit Operation &nbsp;|&nbsp;
**Forms:** 8 &nbsp;|&nbsp;
**Unique mnemonics:** 8

</div>

Bit manipulation operations (scalar forms).

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [BCNT](../instructions/bcnt.md) | `bcnt srcL,  M, N, ->{t, u, Rd}` | 32 | — | Population count. Counts the number of set bits in a register. |
| [BIC](../instructions/bic.md) | `bic SrcL, M, N, ->{t, u, Rd}` | 32 | — | Bit clear / AND-NOT. |
| [BIS](../instructions/bis.md) | `bis SrcL, M, N, ->{t, u, Rd}` | 32 | — | Bit set / OR. |
| [BXS](../instructions/bxs.md) | `bxs SrcL, M, N, ->{t, u, Rd}` | 32 | — | Bit-field extract signed. |
| [BXU](../instructions/bxu.md) | `bxu SrcL, M, N, ->{t, u, Rd}` | 32 | — | Bit-field extract unsigned. |
| [CLZ](../instructions/clz.md) | `clz SrcL,  M, N, ->{t, u, Rd}` | 32 | — | Count leading zeros. |
| [CTZ](../instructions/ctz.md) | `ctz SrcL,  M, N, ->{t, u, Rd}` | 32 | — | Count trailing zeros. |
| [REV](../instructions/rev.md) | `rev SrcL,  M, N, ->{t, u, Rd}` | 32 | — | Bit-reversal operation. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 12: ALU — Arithmetic Logic Unit](../index.md)
- [Encoding formats](../encoding.md)
