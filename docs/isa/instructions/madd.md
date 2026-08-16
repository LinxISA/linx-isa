# MADD

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `madd SrcL, SrcR, SrcD, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_madd.svg" alt="MADD encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Multiply-add: `Dest = SrcD + SrcL * SrcR`.

## Pseudocode (informative)

```c
// Execute MADD as defined by the ALU semantics.
```

## Encoding Notes

- `MADD adds a snapshotted XLEN addend to the low XLEN scalar product modulo 2^PTO_XLEN and publishes the result.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `madd SrcL, SrcR, SrcD, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
