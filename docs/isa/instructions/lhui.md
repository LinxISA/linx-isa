# LHUI

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/lda_base_imm.md">LDA/BASE_IMM</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `lhui [SrcL, simm], ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_lhui.svg" alt="LHUI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

LHUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value.

## Pseudocode (informative)

```c
// Execute LHUI as defined by the LDA/BASE_IMM semantics.
```

## Encoding Notes

- `LHUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `lhui [SrcL, simm], ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [LDA/BASE_IMM](../groups/lda_base_imm.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
