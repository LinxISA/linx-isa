# HL.SW.UPO

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/sta_post_index.md">STA/POST_INDEX</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.sw.upo SrcD, [SrcL, SrcR<{.sw,.uw}>], ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_sw_upo.svg" alt="HL.SW.UPO encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.SW.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value.

## Pseudocode (informative)

```c
// Execute HL.SW.UPO as defined by the STA/POST_INDEX semantics.
```

## Encoding Notes

- `HL.SW.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.sw.upo SrcD, [SrcL, SrcR<{.sw,.uw}>], ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [STA/POST_INDEX](../groups/sta_post_index.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
