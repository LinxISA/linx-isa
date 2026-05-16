# BCNT

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bit_operation.md">Bit Operation</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `bcnt srcL,  M, N, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_bcnt.svg" alt="BCNT encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Population count. Counts the number of set bits in a register.

## Pseudocode (informative)

```c
rd = PopCount(rs1);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `bcnt srcL,  M, N, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [Bit Operation](../groups/bit_operation.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
