# C.SWI

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/store_immediate_offset.md">Store Immediate Offset</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.swi t#1, [srcL, simm]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_swi.svg" alt="C.SWI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[16-bit C.] Stores a register value to memory.

## Pseudocode (informative)

```c
Store(/* addr */, rs2);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.swi t#1, [srcL, simm]` | 16 | — |

<div class="insn-nav">

← [Store Immediate Offset](../groups/store_immediate_offset.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
