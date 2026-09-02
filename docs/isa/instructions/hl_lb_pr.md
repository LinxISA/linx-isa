# HL.LB.PR

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/lda_pre_index.md">LDA/PRE_INDEX</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.lb.pr [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_lb_pr.svg" alt="HL.LB.PR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.LB.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value.

## Pseudocode (informative)

```c
// Execute HL.LB.PR as defined by the LDA/PRE_INDEX semantics.
```

## Encoding Notes

- `HL.LB.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.lb.pr [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [LDA/PRE_INDEX](../groups/lda_pre_index.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
