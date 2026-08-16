# SB.PCR

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/sta.md">STA</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `sb.pcr SrcL, [symbol]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_sb_pcr.svg" alt="SB.PCR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

SB.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value.

## Pseudocode (informative)

```c
// Execute SB.PCR as defined by the STA semantics.
```

## Encoding Notes

- `SB.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `sb.pcr SrcL, [symbol]` | 32 | — |

<div class="insn-nav">

← [STA](../groups/sta.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
