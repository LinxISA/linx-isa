# MADDW

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `maddw SrcL, SrcR, SrcD, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_maddw.svg" alt="MADDW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

32-bit word multiply-add.

## Pseudocode (informative)

```c
// Execute MADDW as defined by the ALU semantics.
```

## Encoding Notes

- `MADDW adds low 32-bit source values modulo 2^32, sign-extends the accumulated result to XLEN, and publishes it.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `maddw SrcL, SrcR, SrcD, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
