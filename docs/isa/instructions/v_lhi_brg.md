# V.LHI.BRG

<div class="insn-header">

<span class="badge-64">64-bit V.</span> **Group:** <a href="../groups/load_immediate_offset.md">Load Immediate Offset</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `v.lhi.brg<.local> [SrcL, <lc0<<1>, simm], ->Dst`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_v_lhi_brg_parts.svg" alt="V.LHI.BRG encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[64-bit V.] Loads a value from memory into a register.

## Pseudocode (informative)

```c
rd = Load(/* addr */);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `v.lhi.brg<.local> [SrcL, <lc0<<1>, simm], ->Dst` | 64 | — |

<div class="insn-nav">

← [Load Immediate Offset](../groups/load_immediate_offset.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
