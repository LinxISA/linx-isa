# PRFI.U

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/lda_unscaled.md">LDA/UNSCALED</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `prfi.u [SrcL, simm]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_prfi_u.svg" alt="PRFI.U encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

PRFI.U snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint with no destination effect.

## Pseudocode (informative)

```c
// Execute PRFI.U as defined by the LDA/UNSCALED semantics.
```

## Encoding Notes

- `PRFI.U snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint with no destination effect.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `prfi.u [SrcL, simm]` | 32 | — |

<div class="insn-nav">

← [LDA/UNSCALED](../groups/lda_unscaled.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
