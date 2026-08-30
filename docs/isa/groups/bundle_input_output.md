# Bundle Input & Output

<div class="insn-header">

<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Group:** Bundle Input & Output &nbsp;|&nbsp;
**Forms:** 7 &nbsp;|&nbsp;
**Unique mnemonics:** 3

</div>

Instructions in the **Bundle Input & Output** group of the LinxISA v0.58.5 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [B.IOR](../instructions/b_ior.md) | `B.IOR [<gpr>[, <gpr>[, <gpr>]]][, -><gpr>]` | 32 | — | Bind up to three absolute GPR inputs and one absolute GPR output; TLOAD/TSTORE use source zero as GM base and source one as byte row stride. |
| [B.IOS](../instructions/b_ios.md) | `B.IOS S<SharedTileID>, mask=<PE_MASK> | B.IOS mask=<PE_MASK>, ->S<SharedTileID><SizeCode>` | 32 | — | Binds one ordered absolute Core-private Shared register S0..S63 as a source or destination with a common four-PE participation mode decoded to a fixed mask. |
| [B.IOT](../instructions/b_iot.md) | `B.IOT SrcTile0, mask=PE_MASK, <last>` | 32 | — | Binds an ordered Local Tile source/destination sequence with one common four-PE participation mode decoded to a fixed mask; L terminates only that sequence and never releases a source. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 4: Block ISA — Block-structured Control Flow](../index.md)
- [Encoding formats](../encoding.md)
