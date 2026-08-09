# HL.DIVW

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/multi_cycle_alu.md">Multi-Cycle ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.divw SrcL, SrcR, ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_divw.svg" alt="HL.DIVW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.DIVW - Compute 32-bit quotient and remainder as a sign-extended result pair.

## Pseudocode (informative)

```c
// Execute HL.DIVW as defined by the Multi-Cycle ALU semantics.
```

## Encoding Notes

- `HL.DIVW - Compute 32-bit quotient and remainder as a sign-extended result pair.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.divw SrcL, SrcR, ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [Multi-Cycle ALU](../groups/multi_cycle_alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
