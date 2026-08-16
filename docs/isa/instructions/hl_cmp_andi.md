# HL.CMP.ANDI

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/bru.md">BRU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.cmp.andi SrcL, simm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_cmp_andi.svg" alt="HL.CMP.ANDI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.CMP.ANDI - Combine scalar comparison results with the encoded logical operation.

## Pseudocode (informative)

```c
// Execute HL.CMP.ANDI as defined by the BRU semantics.
```

## Encoding Notes

- `HL.CMP.ANDI - Combine scalar comparison results with the encoded logical operation.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.cmp.andi SrcL, simm, ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [BRU](../groups/bru.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
