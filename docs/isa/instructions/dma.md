# DMA

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/dma_operation.md">DMA Operation</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `dma [SrcL], SrcR`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_dma.svg" alt="DMA encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Instruction from the DMA Operation group.

## Pseudocode (informative)

```c
// Execute DMA as defined by the DMA Operation semantics.
```

## Encoding Notes

- `v0.57 encoding for the inherited DMA operation: copy 64 bytes from the source address in SrcL to the destination address in SrcR and complete before submission.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `dma [SrcL], SrcR` | 32 | — |

<div class="insn-nav">

← [DMA Operation](../groups/dma_operation.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
