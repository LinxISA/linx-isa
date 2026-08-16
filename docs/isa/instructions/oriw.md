# ORIW

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `oriw SrcL, simm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_oriw.svg" alt="ORIW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

32-bit word OR-immediate.

## Pseudocode (informative)

```c
// Execute ORIW as defined by the ALU semantics.
```

## Encoding Notes

- `ORIW ORs SrcL[31:0] with the low 32 bits of sign-extended simm12, sign-extends the result to XLEN, and publishes it through RegDst.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `oriw SrcL, simm, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
