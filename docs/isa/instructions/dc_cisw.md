# DC.CISW

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/cache_maintain.md">Cache Maintain</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `dc.cisw SrcL`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_dc_cisw.svg" alt="DC.CISW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Data cache clean-and-invalidate by set/way.

## Pseudocode (informative)

```c
// Execute DC.CISW as defined by the Cache Maintain semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `dc.cisw SrcL` | 32 | — |

<div class="insn-nav">

← [Cache Maintain](../groups/cache_maintain.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
