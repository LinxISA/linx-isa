# HL.ADDIW

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.addiw SrcL, uimm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_addiw.svg" alt="HL.ADDIW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.ADDIW applies word addition to SrcL[31:0] and the low word of a zero-extended 24-bit immediate, then sign-extends the 32-bit result.

## Pseudocode (informative)

```c
// Execute HL.ADDIW as defined by the ALU semantics.
```

## Encoding Notes

- `HL.ADDIW applies word addition to SrcL[31:0] and the low word of a zero-extended 24-bit immediate, then sign-extends the 32-bit result.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.addiw SrcL, uimm, ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
