# BC.IVA

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/cache_maintain.md">Cache Maintain</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `bc.iva SrcL`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_bc_iva.svg" alt="BC.IVA encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Branch-predictor cache invalidate by address.

## Pseudocode (informative)

```c
// Execute BC.IVA as defined by the Cache Maintain semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `bc.iva SrcL` | 32 | — |

<div class="insn-nav">

← [Cache Maintain](../groups/cache_maintain.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
