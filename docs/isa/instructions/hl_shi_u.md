# HL.SHI.U

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/sta_long.md">STA/LONG</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.shi.u SrcD, [SrcR, simm]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_shi_u.svg" alt="HL.SHI.U encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.SHI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value.

## Pseudocode (informative)

```c
// Execute HL.SHI.U as defined by the STA/LONG semantics.
```

## Encoding Notes

- `HL.SHI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.shi.u SrcD, [SrcR, simm]` | 48 | — |

<div class="insn-nav">

← [STA/LONG](../groups/sta_long.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
