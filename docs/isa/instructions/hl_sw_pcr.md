# HL.SW.PCR

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/sta_pc_rel.md">STA/PC_REL</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.sw.pcr SrcL, [<symbol>]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_sw_pcr.svg" alt="HL.SW.PCR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.SW.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value.

## Pseudocode (informative)

```c
// Execute HL.SW.PCR as defined by the STA/PC_REL semantics.
```

## Encoding Notes

- `HL.SW.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.sw.pcr SrcL, [<symbol>]` | 48 | — |

<div class="insn-nav">

← [STA/PC_REL](../groups/sta_pc_rel.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
