# DMA Operation

<div class="insn-header">

<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Group:** DMA Operation &nbsp;|&nbsp;
**Forms:** 1 &nbsp;|&nbsp;
**Unique mnemonics:** 1

</div>

Instructions in the **DMA Operation** group of the LinxISA v0.58.0 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [DMA](../instructions/dma.md) | `dma [SrcL], SrcR` | 32 | — | Copies exactly one 64-byte region from the SrcL address to the SrcR address; validates both ranges before effects, snapshots the source so overlap has memmove semantics, and guarantees that a fault leaves memory unchanged. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 0: ISA Manual](../index.md)
- [Encoding formats](../encoding.md)
