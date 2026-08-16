# CASD

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/amo.md">AMO</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `casd<.{aq, rl, aqrl}> [SrcL], SrcR, SrcD, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_casd.svg" alt="CASD encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

CASD atomically compares and conditionally replaces one doubleword, then publishes the prior value.

## Pseudocode (informative)

```c
// Execute CASD as defined by the AMO semantics.
```

## Encoding Notes

- `CASD atomically compares and conditionally replaces one doubleword, then publishes the prior value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `casd<.{aq, rl, aqrl}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [AMO](../groups/amo.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
