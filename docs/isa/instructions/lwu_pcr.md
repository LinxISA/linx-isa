# LWU.PCR

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/lda.md">LDA</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `lwu.pcr [symbol], ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_lwu_pcr.svg" alt="LWU.PCR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

LWU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value.

## Pseudocode (informative)

```c
// Execute LWU.PCR as defined by the LDA semantics.
```

## Encoding Notes

- `LWU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `lwu.pcr [symbol], ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [LDA](../groups/lda.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
