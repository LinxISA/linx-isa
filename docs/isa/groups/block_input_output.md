# Block Input & Output

<div class="insn-header">

<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Group:** Block Input & Output &nbsp;|&nbsp;
**Forms:** 5 &nbsp;|&nbsp;
**Unique mnemonics:** 3

</div>

Block I/O declaration instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [B.IOD](../instructions/b_iod.md) | `B.IOD DepSrc0, DepSrc1, DepSrc2, ->DepDst` | 32 | — | Instruction from the Block Input & Output group. |
| [B.IOR](../instructions/b_ior.md) | `B.IOR [RegSrc0, RegSrc1, RegSrc2],[RegDst]` | 32 | — | Instruction from the Block Input & Output group. |
| [B.IOT](../instructions/b_iot.md) | `B.IOT SrcTile0<.reuse>, <last>, ->DstTile<Size>` | 32 | — | Instruction from the Block Input & Output group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 4: Block ISA — Block-structured Control Flow](../index.md)
- [Encoding formats](../encoding.md)
