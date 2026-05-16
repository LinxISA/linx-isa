# SLLIW

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/arithmetic_operation_32bit.md">Arithmetic Operation 32bit</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `slliw SrcL, shamt, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_slliw.svg" alt="SLLIW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

32-bit word logical left shift (immediate).

## Pseudocode (informative)

```c
// Execute SLLIW as defined by the Arithmetic Operation 32bit semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `slliw SrcL, shamt, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
