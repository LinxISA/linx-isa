# SLL

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `sll SrcL, SrcR, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_sll.svg" alt="SLL encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Logical left shift by the value in SrcR.

## Pseudocode (informative)

```c
rd = rs1 << (rs2 & 63);
```

## Encoding Notes

- `SLL performs a logical left shift of the PTO_XLEN source by the low six bits of the snapshotted SrcR; the XLEN result is published directly.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `sll SrcL, SrcR, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
