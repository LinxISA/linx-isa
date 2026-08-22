# HL.REMUW

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.remuw SrcL, SrcR, ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_remuw.svg" alt="HL.REMUW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.REMUW computes an unsigned low-32-bit remainder/quotient pair from source snapshots, then publishes remainder followed by quotient.

## Pseudocode (informative)

```c
// Execute HL.REMUW as defined by the ALU semantics.
```

## Encoding Notes

- `HL.REMUW computes an unsigned low-32-bit remainder/quotient pair from source snapshots, then publishes remainder followed by quotient.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.remuw SrcL, SrcR, ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
