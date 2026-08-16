# HL.CMP.GEI

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/bru.md">BRU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.cmp.gei SrcL, simm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_cmp_gei.svg" alt="HL.CMP.GEI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.CMP.GEI - Compare scalar operands and write the encoded boolean result.

## Pseudocode (informative)

```c
// Execute HL.CMP.GEI as defined by the BRU semantics.
```

## Encoding Notes

- `HL.CMP.GEI - Compare scalar operands and write the encoded boolean result.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.cmp.gei SrcL, simm, ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [BRU](../groups/bru.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
