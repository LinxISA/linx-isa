# DIV

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/multi_cycle_alu.md">Multi-Cycle ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `div SrcL, SrcR, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_div.svg" alt="DIV encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Signed integer division.

## Pseudocode (informative)

```c
rd = (rs2 != 0) ? (rs1 / rs2) : 0;
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `div SrcL, SrcR, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [Multi-Cycle ALU](../groups/multi_cycle_alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
