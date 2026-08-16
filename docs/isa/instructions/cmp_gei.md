# CMP.GEI

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bru.md">BRU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `cmp.gei SrcL, simm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_cmp_gei.svg" alt="CMP.GEI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

CMP.GEI - Compare scalar operands and write the encoded boolean result.

## Pseudocode (informative)

```c
// Execute CMP.GEI as defined by the BRU semantics.
```

## Encoding Notes

- `CMP.GEI - Compare scalar operands and write the encoded boolean result.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `cmp.gei SrcL, simm, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [BRU](../groups/bru.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
