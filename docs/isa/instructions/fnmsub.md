# FNMSUB

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/fsu.md">FSU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-13">Ch 13</span>
&nbsp; <strong>FSU — Floating-point / SIMD Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `fnmsub.{T} SrcL, SrcR, SrcA, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_fnmsub.svg" alt="FNMSUB encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

FNMSUB computes the negation of one fused SrcL multiplied by SrcR minus SrcA operation through the active numeric profile.

## Pseudocode (informative)

```c
// Execute FNMSUB as defined by the FSU semantics.
```

## Encoding Notes

- `FNMSUB computes the negation of one fused SrcL multiplied by SrcR minus SrcA operation through the active numeric profile.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `fnmsub.{T} SrcL, SrcR, SrcA, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [FSU](../groups/fsu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
