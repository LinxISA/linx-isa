# MAXU

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `maxu SrcL, SrcR, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_maxu.svg" alt="MAXU encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

MAXU performs an unsigned full-XLEN comparison and publishes the complete bit pattern of the maximum operand.

## Pseudocode (informative)

```c
// Execute MAXU as defined by the ALU semantics.
```

## Encoding Notes

- `MAXU performs an unsigned full-XLEN comparison and publishes the complete bit pattern of the maximum operand.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `maxu SrcL, SrcR, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
