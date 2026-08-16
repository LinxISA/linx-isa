# LD.UMAX

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/amo.md">AMO</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `ld.umax<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_ld_umax.svg" alt="LD.UMAX encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

LD.UMAX atomically stores the width-sized unsigned maximum and publishes the prior memory value.

## Pseudocode (informative)

```c
// Execute LD.UMAX as defined by the AMO semantics.
```

## Encoding Notes

- `LD.UMAX atomically stores the width-sized unsigned maximum and publishes the prior memory value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `ld.umax<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — |

<div class="insn-nav">

← [AMO](../groups/amo.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
