# CSEL

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
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

- `CSEL snapshots three Reg5 sources, selects SrcL for a nonzero predicate or its optionally negated SrcR for zero, and publishes through the common scalar destination map.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `csel SrcP, SrcL, SrcR<.neg>, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
