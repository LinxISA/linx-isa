# SC.D

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/amo.md">AMO</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `sc.d<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> SrcL, [SrcR], {->t, ->u, ->Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_sc_d.svg" alt="SC.D encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

SC.D conditionally stores one doubleword when the local 64-byte-line reservation matches.

## Pseudocode (informative)

```c
// Execute SC.D as defined by the AMO semantics.
```

## Encoding Notes

- `SC.D conditionally stores one doubleword when the local 64-byte-line reservation matches.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `sc.d<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> SrcL, [SrcR], {->t, ->u, ->Rd}` | 32 | — |

<div class="insn-nav">

← [AMO](../groups/amo.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
