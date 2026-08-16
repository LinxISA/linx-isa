# C.SETRET

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.setret uimm, ->ra`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_setret.svg" alt="C.SETRET encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Materialize an unsigned halfword-scaled TPC-relative return address in ra and captured return state.

## Pseudocode (informative)

```c
ra = PC + ZeroExtend(imm << 1);
```

## Encoding Notes

- `Materialize an unsigned halfword-scaled TPC-relative return address in ra and captured return state.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.setret uimm, ->ra` | 16 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
