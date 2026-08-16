# C.CMP.EQI

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/bru.md">BRU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.cmp.eqi t#1, simm, ->t`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_cmp_eqi.svg" alt="C.CMP.EQI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

C.CMP.EQI - Compare scalar operands and write the encoded boolean result.

## Pseudocode (informative)

```c
// Execute C.CMP.EQI as defined by the BRU semantics.
```

## Encoding Notes

- `C.CMP.EQI - Compare scalar operands and write the encoded boolean result.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.cmp.eqi t#1, simm, ->t` | 16 | — |

<div class="insn-nav">

← [BRU](../groups/bru.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
