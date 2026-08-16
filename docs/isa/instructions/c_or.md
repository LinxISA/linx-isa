# C.OR

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.or srcL, srcR, ->t`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_or.svg" alt="C.OR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[16-bit C.] Bitwise OR.

## Pseudocode (informative)

```c
rd = rs1 | rs2;
```

## Encoding Notes

- `C.OR snapshots two complete Reg5 sources, computes the bitwise inclusive OR of SrcL and SrcR, and pushes the wrapping XLEN result to T.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.or srcL, srcR, ->t` | 16 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
