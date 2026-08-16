# HL.LBI.PR

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/lda_pre_index.md">LDA/PRE_INDEX</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.lbi.pr [SrcL, simm], ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_lbi_pr.svg" alt="HL.LBI.PR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.LBI.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value.

## Pseudocode (informative)

```c
// Execute HL.LBI.PR as defined by the LDA/PRE_INDEX semantics.
```

## Encoding Notes

- `HL.LBI.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.lbi.pr [SrcL, simm], ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [LDA/PRE_INDEX](../groups/lda_pre_index.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
