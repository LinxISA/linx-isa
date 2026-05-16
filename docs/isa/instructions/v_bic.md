# V.BIC

<div class="insn-header">

<span class="badge-64">64-bit V.</span> **Group:** <a href="../groups/bit_manipulation.md">Bit Manipulation</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `v.bic SrcL, M, N, ->Dst`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_v_bic_parts.svg" alt="V.BIC encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[64-bit V.] Bit clear.

## Pseudocode (informative)

```c
// Execute V.BIC as defined by the Bit Manipulation semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `v.bic SrcL, M, N, ->Dst` | 64 | — |

<div class="insn-nav">

← [Bit Manipulation](../groups/bit_manipulation.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
