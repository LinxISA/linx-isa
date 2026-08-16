# FCVTA

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/fsu.md">FSU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-13">Ch 13</span>
&nbsp; <strong>FSU — Floating-point / SIMD Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `fcvta.{srcT2dstT} SrcL, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_fcvta.svg" alt="FCVTA encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

FCVTA converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-away mode.

## Pseudocode (informative)

```c
// Execute FCVTA as defined by the FSU semantics.
```

## Encoding Notes

- `FCVTA converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-away mode.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `fcvta.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [FSU](../groups/fsu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
