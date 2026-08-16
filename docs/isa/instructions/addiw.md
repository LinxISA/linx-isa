# ADDIW

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `addiw SrcL, uimm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_addiw.svg" alt="ADDIW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

32-bit word add-immediate.

## Pseudocode (informative)

```c
// Execute ADDIW as defined by the ALU semantics.
```

## Encoding Notes

- `ADDIW adds the zero-extended unsigned 12-bit immediate to SrcL[31:0] modulo 2^32, sign-extends the word result to XLEN, and publishes it through RegDst.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `addiw SrcL, uimm, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
