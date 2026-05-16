# V.LH

<div class="insn-header">

<span class="badge-64">64-bit V.</span> **Group:** <a href="../groups/load_register_offset.md">Load Register Offset</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `v.lh<.local> [SrcL, <lc0<<1>, SrcR<<<shamt>], ->Dst`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_v_lh_parts.svg" alt="V.LH encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[64-bit V.] Loads a signed 16-bit value from memory.

## Pseudocode (informative)

```c
rd = Load(/* addr */);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `v.lh<.local> [SrcL, <lc0<<1>, SrcR<<<shamt>], ->Dst` | 64 | — |

<div class="insn-nav">

← [Load Register Offset](../groups/load_register_offset.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
