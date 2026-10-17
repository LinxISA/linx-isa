# DMA.FREE.S

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/amo.md">AMO</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `dma.free.s [SrcL]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_dma_free_s.svg" alt="DMA.FREE.S encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Encoding only; NOT IMPLEMENTED. The encoding and operand fields are reserved for DMA.FREE.S. Execution is unsupported and must reject before operand reads or architectural effects. No copy, replica allocation, release, return-address, or completion semantics are implemented.

## Pseudocode (informative)

```c
raise IllegalInstruction; // encoding only, NOT IMPLEMENTED; no operand reads or effects
```

## Encoding Notes

- `Encoding only; NOT IMPLEMENTED. The encoding and operand fields are reserved for DMA.FREE.S. Execution is unsupported and must reject before operand reads or architectural effects. No copy, replica allocation, release, return-address, or completion semantics are implemented.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `dma.free.s [SrcL]` | 32 | — |

<div class="insn-nav">

← [AMO](../groups/amo.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
