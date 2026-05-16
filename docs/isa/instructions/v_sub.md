# V.SUB

<div class="insn-header">

<span class="badge-64">64-bit V.</span> **Group:** <a href="../groups/arithmetic_operation.md">Arithmetic Operation</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `v.sub SrcL, SrcR<.neg><<<shamt>, ->Dst`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_v_sub_parts.svg" alt="V.SUB encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[64-bit V.] Integer subtraction.

## Pseudocode (informative)

```c
rd = rs1 - rs2;
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `v.sub SrcL, SrcR<.neg><<<shamt>, ->Dst` | 64 | — |

<div class="insn-nav">

← [Arithmetic Operation](../groups/arithmetic_operation.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
