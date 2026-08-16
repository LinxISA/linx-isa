# Bundle Dimension

<div class="insn-header">

<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Group:** Bundle Dimension &nbsp;|&nbsp;
**Forms:** 1 &nbsp;|&nbsp;
**Unique mnemonics:** 1

</div>

Instructions in the **Bundle Dimension** group of the LinxISA v0.58.1 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [C.B.DIMI](../instructions/c_b_dimi.md) | `C.B.DIMI imm, ->{LB0, LB1, LB2}` | 16 | — | Zero-extends imm8 and writes one selected bundle-local LB exactly once. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 4: Block ISA — Block-structured Control Flow](../index.md)
- [Encoding formats](../encoding.md)
