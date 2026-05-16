# ADDI

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/arithmetic_operation_64bit.md">Arithmetic Operation 64bit</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `addi SrcL, uimm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_addi.svg" alt="ADDI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Integer add-immediate. Adds a sign-extended 12-bit immediate to a register.

## Pseudocode (informative)

```c
rd = rs1 + SignExtend(imm12);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `addi SrcL, uimm, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
