# Bundle Argument

<div class="insn-header">

<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Group:** Bundle Argument &nbsp;|&nbsp;
**Forms:** 3 &nbsp;|&nbsp;
**Unique mnemonics:** 1

</div>

Instructions in the **Bundle Argument** group of the LinxISA v0.58.1 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [B.DIM](../instructions/b_dim.md) | `B.DIM RegSrc, uimm, ->LB1` | 32 | — | Writes zero-extend((GPR[RegSrc] + uimm17)[15:0]) to the selected bundle-local LB register exactly once. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 4: Block ISA — Block-structured Control Flow](../index.md)
- [Encoding formats](../encoding.md)
