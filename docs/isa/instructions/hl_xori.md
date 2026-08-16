# HL.XORI

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.xori SrcL, simm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_xori.svg" alt="HL.XORI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.XORI applies XLEN bitwise exclusive-or to SrcL and a sign-extended 24-bit immediate.

## Pseudocode (informative)

```c
rd = rs1 ^ SignExtend(imm12);
```

## Encoding Notes

- `HL.XORI applies XLEN bitwise exclusive-or to SrcL and a sign-extended 24-bit immediate.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.xori SrcL, simm, ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
