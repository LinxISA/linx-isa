# HL.REMW

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.remw SrcL, SrcR, ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_remw.svg" alt="HL.REMW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.REMW computes a signed low-32-bit remainder/quotient pair from source snapshots, then publishes remainder followed by quotient.

## Pseudocode (informative)

```c
// Execute HL.REMW as defined by the ALU semantics.
```

## Encoding Notes

- `HL.REMW computes a signed low-32-bit remainder/quotient pair from source snapshots, then publishes remainder followed by quotient.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.remw SrcL, SrcR, ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
