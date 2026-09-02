# HL.SH.PO

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/sta_post_index.md">STA/POST_INDEX</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.sh.po SrcD, [SrcL, SrcR<{.sw,.uw}><<1], ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_sh_po.svg" alt="HL.SH.PO encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.SH.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value.

## Pseudocode (informative)

```c
// Execute HL.SH.PO as defined by the STA/POST_INDEX semantics.
```

## Encoding Notes

- `HL.SH.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.sh.po SrcD, [SrcL, SrcR<{.sw,.uw}><<1], ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [STA/POST_INDEX](../groups/sta_post_index.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
