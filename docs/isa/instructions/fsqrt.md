# FSQRT

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/fsu.md">FSU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-13">Ch 13</span>
&nbsp; <strong>FSU — Floating-point / SIMD Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `fsqrt.{T} SrcL, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_fsqrt.svg" alt="FSQRT encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Floating-point square root.

## Pseudocode (informative)

```c
// Execute FSQRT as defined by the FSU semantics.
```

## Encoding Notes

- `FSQRT applies the active numeric profile square-root operation to the selected FP64 or FP32 carrier.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `fsqrt.{T} SrcL, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [FSU](../groups/fsu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
