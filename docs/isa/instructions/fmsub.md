# FMSUB

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/fsu.md">FSU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-13">Ch 13</span>
&nbsp; <strong>FSU — Floating-point / SIMD Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `fmsub.{T} SrcL, SrcR, SrcA, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_fmsub.svg" alt="FMSUB encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

FMSUB computes one fused SrcL multiplied by SrcR minus SrcA operation through the active numeric profile.

## Pseudocode (informative)

```c
// Execute FMSUB as defined by the FSU semantics.
```

## Encoding Notes

- `FMSUB computes one fused SrcL multiplied by SrcR minus SrcA operation through the active numeric profile.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `fmsub.{T} SrcL, SrcR, SrcA, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [FSU](../groups/fsu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
