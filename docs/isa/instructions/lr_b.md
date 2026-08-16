# LR.B

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/amo.md">AMO</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `lr.b<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], {->t, ->u, ->Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_lr_b.svg" alt="LR.B encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

LR.B loads one byte, establishes a 64-byte-line reservation, and publishes the prior value.

## Pseudocode (informative)

```c
// Execute LR.B as defined by the AMO semantics.
```

## Encoding Notes

- `LR.B loads one byte, establishes a 64-byte-line reservation, and publishes the prior value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `lr.b<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], {->t, ->u, ->Rd}` | 32 | — |

<div class="insn-nav">

← [AMO](../groups/amo.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
