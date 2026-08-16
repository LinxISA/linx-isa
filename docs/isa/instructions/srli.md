# SRLI

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `srli SrcL, shamt, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_srli.svg" alt="SRLI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Logical right shift by an immediate amount.

## Pseudocode (informative)

```c
rd = rs1 >> shamt (logical);
```

## Encoding Notes

- `SRLI logically shifts the snapshotted XLEN source right by the encoded six-bit amount and publishes the XLEN result through RegDst.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `srli SrcL, shamt, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
