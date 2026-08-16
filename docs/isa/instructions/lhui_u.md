# LHUI.U

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/lda_unscaled.md">LDA/UNSCALED</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `lhui.u [SrcL, simm], ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_lhui_u.svg" alt="LHUI.U encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

LHUI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value.

## Pseudocode (informative)

```c
// Execute LHUI.U as defined by the LDA/UNSCALED semantics.
```

## Encoding Notes

- `LHUI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `lhui.u [SrcL, simm], ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [LDA/UNSCALED](../groups/lda_unscaled.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
