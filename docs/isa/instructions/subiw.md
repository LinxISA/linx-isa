# SUBIW

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `subiw SrcL, uimm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_subiw.svg" alt="SUBIW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

SUBIW subtracts the zero-extended unsigned 12-bit immediate from SrcL[31:0] modulo 2^32, sign-extends the word result to XLEN, and publishes it through RegDst.

## Pseudocode (informative)

```c
// Execute SUBIW as defined by the ALU semantics.
```

## Encoding Notes

- `SUBIW subtracts the zero-extended unsigned 12-bit immediate from SrcL[31:0] modulo 2^32, sign-extends the word result to XLEN, and publishes it through RegDst.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `subiw SrcL, uimm, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
