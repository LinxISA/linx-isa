# C.SLLI

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.slli t#1, uimm, ->t`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_slli.svg" alt="C.SLLI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

C.SLLI snapshots the pre-instruction T#1 value, logically shifts it left by uimm5, and pushes the XLEN result to T.

## Pseudocode (informative)

```c
rd = rs1 << shamt;
```

## Encoding Notes

- `C.SLLI snapshots the pre-instruction T#1 value, logically shifts it left by uimm5, and pushes the XLEN result to T.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.slli t#1, uimm, ->t` | 16 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
