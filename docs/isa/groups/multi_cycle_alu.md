# Multi-Cycle ALU

<div class="insn-header">

<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Group:** Multi-Cycle ALU &nbsp;|&nbsp;
**Forms:** 2 &nbsp;|&nbsp;
**Unique mnemonics:** 2

</div>

Multi-cycle ALU operations: division, remainder, and extended multiply.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [V.MADD](../instructions/v_madd.md) | `v.madd SrcL, SrcR, SrcD, ->Dst` | 64 | — | [64-bit V.] Instruction from the Multi-Cycle ALU group. |
| [V.MUL](../instructions/v_mul.md) | `v.mul SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Integer multiply. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 12: ALU — Arithmetic Logic Unit](../index.md)
- [Encoding formats](../encoding.md)
