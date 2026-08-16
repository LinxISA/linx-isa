# MINU

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `minu SrcL, SrcR, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_minu.svg" alt="MINU encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

MINU performs an unsigned full-XLEN comparison and publishes the complete bit pattern of the minimum operand.

## Pseudocode (informative)

```c
// Execute MINU as defined by the ALU semantics.
```

## Encoding Notes

- `MINU performs an unsigned full-XLEN comparison and publishes the complete bit pattern of the minimum operand.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `minu SrcL, SrcR, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
