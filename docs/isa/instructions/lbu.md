# LBU

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/lda_base_reg.md">LDA/BASE_REG</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `lbu [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_lbu.svg" alt="LBU encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

LBU snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value.

## Pseudocode (informative)

```c
// Execute LBU as defined by the LDA/BASE_REG semantics.
```

## Encoding Notes

- `LBU snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `lbu [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [LDA/BASE_REG](../groups/lda_base_reg.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
