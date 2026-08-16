# HL.LHU.PO

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/lda_post_index.md">LDA/POST_INDEX</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.lhu.po [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_lhu_po.svg" alt="HL.LHU.PO encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.LHU.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value.

## Pseudocode (informative)

```c
// Execute HL.LHU.PO as defined by the LDA/POST_INDEX semantics.
```

## Encoding Notes

- `HL.LHU.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.lhu.po [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [LDA/POST_INDEX](../groups/lda_post_index.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
