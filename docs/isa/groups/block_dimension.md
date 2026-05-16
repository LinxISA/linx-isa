# Block Dimension

<div class="insn-header">

<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Group:** Block Dimension &nbsp;|&nbsp;
**Forms:** 2 &nbsp;|&nbsp;
**Unique mnemonics:** 2

</div>

Instructions that set block loop-dimension registers.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [C.B.DIM](../instructions/c_b_dim.md) | `C.B.DIM RegSrc, ->{LB0, LB1, LB2}` | 16 | — | [16-bit C.] Instruction from the Block Dimension group. |
| [C.B.DIMI](../instructions/c_b_dimi.md) | `C.B.DIMI imm, ->{LB0, LB1, LB2}` | 16 | — | [16-bit C.] Instruction from the Block Dimension group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 4: Block ISA — Block-structured Control Flow](../index.md)
- [Encoding formats](../encoding.md)
