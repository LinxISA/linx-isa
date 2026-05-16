# SB

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/store_register_offset.md">Store Register Offset</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `sb SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_sb.svg" alt="SB encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Stores a register value to memory.

## Pseudocode (informative)

```c
Store(/* addr */, rs2);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `sb SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 32 | — |

<div class="insn-nav">

← [Store Register Offset](../groups/store_register_offset.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
