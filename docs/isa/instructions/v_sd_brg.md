# V.SD.BRG

<div class="insn-header">

<span class="badge-64">64-bit V.</span> **Group:** <a href="../groups/store_register_offset.md">Store Register Offset</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `v.sd.brg<.local> SrcD.<T1>, [SrcL, <lc0<<3>, SrcR.<T2><<(3+shamt)]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_v_sd_brg_parts.svg" alt="V.SD.BRG encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[64-bit V.] Stores a register value to memory.

## Pseudocode (informative)

```c
Store(/* addr */, rs2);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `v.sd.brg<.local> SrcD.<T1>, [SrcL, <lc0<<3>, SrcR.<T2><<(3+shamt)]` | 64 | — |

<div class="insn-nav">

← [Store Register Offset](../groups/store_register_offset.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
