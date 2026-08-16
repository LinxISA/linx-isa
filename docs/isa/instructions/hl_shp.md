# HL.SHP

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/sta_pair.md">STA/PAIR</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.shp SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}><<1]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_shp.svg" alt="HL.SHP encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.SHP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 2-byte values.

## Pseudocode (informative)

```c
// Execute HL.SHP as defined by the STA/PAIR semantics.
```

## Encoding Notes

- `HL.SHP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 2-byte values.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.shp SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}><<1]` | 48 | — |

<div class="insn-nav">

← [STA/PAIR](../groups/sta_pair.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
