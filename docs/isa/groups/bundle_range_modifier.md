# Bundle Range Modifier

<div class="insn-header">

<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Group:** Bundle Range Modifier &nbsp;|&nbsp;
**Forms:** 2 &nbsp;|&nbsp;
**Unique mnemonics:** 2

</div>

Instructions in the **Bundle Range Modifier** group of the LinxISA v0.58.5 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [B.ASSEMBLE](../instructions/b_assemble.md) | `B.ASSEMBLE INIT, LAST, RegSrc, uimm11, ParentSizeCode` | 32 | — | Decodes one destination-range assemble modifier and retains its XLEN-wrapped derived offset in the immediately preceding binder group. |
| [B.SUBVIEW](../instructions/b_subview.md) | `B.SUBVIEW SrcSelect, RegSrc, uimm11, SubviewSizeCode` | 32 | — | Decodes one source-range subview modifier and retains its XLEN-wrapped derived offset in the immediately preceding binder group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 4: Block ISA — Block-structured Control Flow](../index.md)
- [Encoding formats](../encoding.md)
