# HL.SUBI

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.subi SrcL, uimm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_subi.svg" alt="HL.SUBI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.SUBI applies XLEN subtraction to SrcL and a zero-extended 24-bit immediate.

## Pseudocode (informative)

```c
// Execute HL.SUBI as defined by the ALU semantics.
```

## Encoding Notes

- `HL.SUBI applies XLEN subtraction to SrcL and a zero-extended 24-bit immediate.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.subi SrcL, uimm, ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
