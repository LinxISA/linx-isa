# HL.LW.PO

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/lda_post_index.md">LDA/POST_INDEX</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.lw.po [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_lw_po.svg" alt="HL.LW.PO encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.LW.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value.

## Pseudocode (informative)

```c
// Execute HL.LW.PO as defined by the LDA/POST_INDEX semantics.
```

## Encoding Notes

- `HL.LW.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.lw.po [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [LDA/POST_INDEX](../groups/lda_post_index.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
