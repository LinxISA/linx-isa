# FEXP

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/floating_point_arithmetic.md">Floating-point Arithmetic</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-13">Ch 13</span>
&nbsp; <strong>FSU — Floating-point / SIMD Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `fexp.{T} SrcL, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_fexp.svg" alt="FEXP encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

FEXP - Compute this mnemonic's unary floating-point operation.

## Pseudocode (informative)

```c
// Execute FEXP as defined by the Floating-point Arithmetic semantics.
```

## Encoding Notes

- `FEXP - Compute this mnemonic's unary floating-point operation.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `fexp.{T} SrcL, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
