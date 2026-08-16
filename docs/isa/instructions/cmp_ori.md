# CMP.ORI

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bru.md">BRU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `cmp.ori SrcL, simm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_cmp_ori.svg" alt="CMP.ORI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

CMP.ORI - Combine scalar comparison results with the encoded logical operation.

## Pseudocode (informative)

```c
// Execute CMP.ORI as defined by the BRU semantics.
```

## Encoding Notes

- `CMP.ORI - Combine scalar comparison results with the encoded logical operation.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `cmp.ori SrcL, simm, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [BRU](../groups/bru.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
