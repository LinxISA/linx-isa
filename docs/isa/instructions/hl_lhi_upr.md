# HL.LHI.UPR

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/lda_pre_index.md">LDA/PRE_INDEX</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.lhi.upr [SrcL, simm], ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_lhi_upr.svg" alt="HL.LHI.UPR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.LHI.UPR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value.

## Pseudocode (informative)

```c
// Execute HL.LHI.UPR as defined by the LDA/PRE_INDEX semantics.
```

## Encoding Notes

- `HL.LHI.UPR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.lhi.upr [SrcL, simm], ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [LDA/PRE_INDEX](../groups/lda_pre_index.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
