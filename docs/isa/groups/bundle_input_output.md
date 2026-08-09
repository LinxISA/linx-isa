# Bundle Input & Output

<div class="insn-header">

<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Group:** Bundle Input & Output &nbsp;|&nbsp;
**Forms:** 7 &nbsp;|&nbsp;
**Unique mnemonics:** 3

</div>

Instructions in the **Bundle Input & Output** group of the LinxISA v0.58.0 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [B.IOR](../instructions/b_ior.md) | `B.IOR [<gpr>[, <gpr>[, <gpr>]]][, -><gpr>]` | 32 | — | Bind up to three absolute GPR inputs and one absolute GPR output; TLOAD/TSTORE use source zero as GM base and source one as logical row stride. |
| [B.IOS](../instructions/b_ios.md) | `B.IOS S<SharedTID>, mask=<PE_MASK> | B.IOS mask=<PE_MASK>, ->S<SharedTID><TSize>` | 32 | — | Binds one ordered absolute core-private Shared register S0..S255 with a per-PE source/destination size code and four-PE participation mask. |
| [B.IOT](../instructions/b_iot.md) | `B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>` | 32 | — | Binds v5 PE_MASK, ordered Local tile sources, last-use, and optional TSize/2-bit Local destination metadata; reuse bits do not exist. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 0: ISA Manual](../index.md)
- [Encoding formats](../encoding.md)
