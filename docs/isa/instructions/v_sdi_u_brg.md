# V.SDI.U.BRG

<div class="insn-header">

<span class="badge-64">64-bit V.</span> **Group:** <a href="../groups/store_offset.md">Store Offset</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `v.sdi.u.brg<.local> SrcL, [SrcR, <lc0<<3>, simm]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_v_sdi_u_brg_parts.svg" alt="V.SDI.U.BRG encoding" width="100%" />
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
| `v.sdi.u.brg<.local> SrcL, [SrcR, <lc0<<3>, simm]` | 64 | — |

<div class="insn-nav">

← [Store Offset](../groups/store_offset.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
