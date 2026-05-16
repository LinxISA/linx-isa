# V.SRL

<div class="insn-header">

<span class="badge-64">64-bit V.</span> **Group:** <a href="../groups/arithmetic_operation.md">Arithmetic Operation</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `v.srl SrcL, SrcR, ->Dst`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_v_srl_parts.svg" alt="V.SRL encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[64-bit V.] Logical right shift.

## Pseudocode (informative)

```c
rd = rs1 >> rs2 (logical);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `v.srl SrcL, SrcR, ->Dst` | 64 | — |

<div class="insn-nav">

← [Arithmetic Operation](../groups/arithmetic_operation.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
