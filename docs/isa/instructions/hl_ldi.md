# HL.LDI

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/lda_long.md">LDA/LONG</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.ldi [SrcL, simm], ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_ldi.svg" alt="HL.LDI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.LDI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value.

## Pseudocode (informative)

```c
// Execute HL.LDI as defined by the LDA/LONG semantics.
```

## Encoding Notes

- `HL.LDI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.ldi [SrcL, simm], ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [LDA/LONG](../groups/lda_long.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
