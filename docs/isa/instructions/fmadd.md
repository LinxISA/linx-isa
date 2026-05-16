# FMADD

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/floating_point_arithmetic.md">Floating-point Arithmetic</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-13">Ch 13</span>
&nbsp; <strong>FSU — Floating-point / SIMD Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `fmadd.{T} SrcL, SrcR, SrcA, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_fmadd.svg" alt="FMADD encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Instruction from the Floating-point Arithmetic group.

## Pseudocode (informative)

```c
// Execute FMADD as defined by the Floating-point Arithmetic semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `fmadd.{T} SrcL, SrcR, SrcA, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
