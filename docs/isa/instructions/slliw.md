# SLLIW

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `slliw SrcL, shamt, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_slliw.svg" alt="SLLIW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

32-bit word logical left shift (immediate).

## Pseudocode (informative)

```c
// Execute SLLIW as defined by the ALU semantics.
```

## Encoding Notes

- `SLLIW logically shifts SrcL[31:0] left by the encoded five-bit amount, sign-extends the word result to XLEN, and publishes it.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `slliw SrcL, shamt, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
