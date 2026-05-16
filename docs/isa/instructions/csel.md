# CSEL

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/compound_operation.md">Compound Operation</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `csel SrcP, SrcL, SrcR<.neg>, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_csel.svg" alt="CSEL encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Conditional select. `Dest = (SrcP != 0) ? SrcL : SrcR`.

## Pseudocode (informative)

```c
rd = (rs_p != 0) ? rs1 : rs2;
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `csel SrcP, SrcL, SrcR<.neg>, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [Compound Operation](../groups/compound_operation.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
