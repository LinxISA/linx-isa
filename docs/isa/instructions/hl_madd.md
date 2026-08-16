# HL.MADD

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.madd SrcL, SrcR, SrcD, ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_madd.svg" alt="HL.MADD encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.MADD computes a signed 128-bit product plus a sign-extended XLEN addend and publishes low then high halves.

## Pseudocode (informative)

```c
// Execute HL.MADD as defined by the ALU semantics.
```

## Encoding Notes

- `HL.MADD computes a signed 128-bit product plus a sign-extended XLEN addend and publishes low then high halves.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.madd SrcL, SrcR, SrcD, ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
