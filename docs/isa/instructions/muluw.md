# MULUW

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `muluw SrcL, SrcR, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_muluw.svg" alt="MULUW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

32-bit word integer multiply (unsigned).

## Pseudocode (informative)

```c
// Execute MULUW as defined by the ALU semantics.
```

## Encoding Notes

- `MULUW multiplies the source low 32-bit values, retains the low 32 product bits, sign-extends them to XLEN, and publishes the result.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `muluw SrcL, SrcR, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
