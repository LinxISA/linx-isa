# Bit Manipulation

<div class="insn-header">

<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Group:** Bit Manipulation &nbsp;|&nbsp;
**Forms:** 8 &nbsp;|&nbsp;
**Unique mnemonics:** 8

</div>

Bit manipulation operations (vector forms).

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [V.BCNT](../instructions/v_bcnt.md) | `v.bcnt SrcL, M, N, ->Dst` | 64 | — | [64-bit V.] Population count. |
| [V.BIC](../instructions/v_bic.md) | `v.bic SrcL, M, N, ->Dst` | 64 | — | [64-bit V.] Bit clear. |
| [V.BIS](../instructions/v_bis.md) | `v.bis SrcL, M, N, ->Dst` | 64 | — | [64-bit V.] Bit set. |
| [V.BXS](../instructions/v_bxs.md) | `v.bxs SrcL, M, N, ->Dst` | 64 | — | [64-bit V.] Bit-field extract signed. |
| [V.BXU](../instructions/v_bxu.md) | `v.bxu SrcL, M, N, ->Dst` | 64 | — | [64-bit V.] Bit-field extract unsigned. |
| [V.CLZ](../instructions/v_clz.md) | `v.clz SrcL, M, N, ->Dst` | 64 | — | [64-bit V.] Count leading zeros. |
| [V.CTZ](../instructions/v_ctz.md) | `v.ctz SrcL, M, N, ->Dst` | 64 | — | [64-bit V.] Count trailing zeros. |
| [V.REV](../instructions/v_rev.md) | `v.rev SrcL, M, N, ->Dst` | 64 | — | [64-bit V.] Bit-reversal. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 12: ALU — Arithmetic Logic Unit](../index.md)
- [Encoding formats](../encoding.md)
