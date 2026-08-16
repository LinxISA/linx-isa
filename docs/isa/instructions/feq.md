# FEQ

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/fsu.md">FSU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-13">Ch 13</span>
&nbsp; <strong>FSU — Floating-point / SIMD Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `feq.{T} SrcL, SrcR, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_feq.svg" alt="FEQ encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Floating-point equality comparison. Writes 1 if ordered and equal.

## Pseudocode (informative)

```c
rd = (fs1 == fs2) ? 1 : 0;
```

## Encoding Notes

- `FEQ performs ordered quiet equality and returns canonical XLEN zero or one.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `feq.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [FSU](../groups/fsu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
