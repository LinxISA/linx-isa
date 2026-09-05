# UCVTF

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/fsu.md">FSU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-13">Ch 13</span>
&nbsp; <strong>FSU — Floating-point / SIMD Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `ucvtf.{srcT2dstT} SrcL, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_ucvtf.svg" alt="UCVTF encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

UCVTF converts a U64, U32, U16, or U8 source to FP64, FP32, FP16, or E4M3 through the common scalar/TCVT profile.

## Pseudocode (informative)

```c
// Execute UCVTF as defined by the FSU semantics.
```

## Encoding Notes

- `UCVTF converts a U64, U32, U16, or U8 source to FP64, FP32, FP16, or E4M3 through the common scalar/TCVT profile.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `ucvtf.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [FSU](../groups/fsu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
