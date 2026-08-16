# FCVTP

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/fsu.md">FSU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-13">Ch 13</span>
&nbsp; <strong>FSU — Floating-point / SIMD Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `fcvtp.{srcT2dstT} SrcL, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_fcvtp.svg" alt="FCVTP encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

FCVTP converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-up mode.

## Pseudocode (informative)

```c
// Execute FCVTP as defined by the FSU semantics.
```

## Encoding Notes

- `FCVTP converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-up mode.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `fcvtp.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [FSU](../groups/fsu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
