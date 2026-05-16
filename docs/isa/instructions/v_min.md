# V.MIN

<div class="insn-header">

<span class="badge-64">64-bit V.</span> **Group:** <a href="../groups/two_source_floating_point.md">Two-Source Floating Point</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-20">Ch 20</span>
&nbsp; <strong>VEC — Vector / SIMD Execution (lx64)</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `v.min SrcL, SrcR, ->Dst`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_v_min_parts.svg" alt="V.MIN encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[64-bit V.] Instruction from the Two-Source Floating Point group.

## Pseudocode (informative)

```c
// Execute V.MIN as defined by the Two-Source Floating Point semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `v.min SrcL, SrcR, ->Dst` | 64 | — |

<div class="insn-nav">

← [Two-Source Floating Point](../groups/two_source_floating_point.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
