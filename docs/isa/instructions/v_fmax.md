# V.FMAX

<div class="insn-header">

<span class="badge-64">64-bit V.</span> **Group:** <a href="../groups/two_source_floating_point.md">Two-Source Floating Point</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-20">Ch 20</span>
&nbsp; <strong>VEC — Vector / SIMD Execution (lx64)</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `v.fmax SrcL, SrcR, ->Dst`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_v_fmax_parts.svg" alt="V.FMAX encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[64-bit V.] Instruction from the Two-Source Floating Point group.

## Pseudocode (informative)

```c
rd = fmax(fs1, fs2);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `v.fmax SrcL, SrcR, ->Dst` | 64 | — |

<div class="insn-nav">

← [Two-Source Floating Point](../groups/two_source_floating_point.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
