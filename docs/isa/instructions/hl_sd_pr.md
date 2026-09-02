# HL.SD.PR

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/sta_pre_index.md">STA/PRE_INDEX</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.sd.pr SrcD, [SrcL, SrcR<{.sw,.uw}><<3], ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_sd_pr.svg" alt="HL.SD.PR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.SD.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value.

## Pseudocode (informative)

```c
// Execute HL.SD.PR as defined by the STA/PRE_INDEX semantics.
```

## Encoding Notes

- `HL.SD.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.sd.pr SrcD, [SrcL, SrcR<{.sw,.uw}><<3], ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [STA/PRE_INDEX](../groups/sta_pre_index.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
