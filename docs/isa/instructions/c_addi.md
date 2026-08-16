# C.ADDI

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.addi srcL, simm, ->t`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_addi.svg" alt="C.ADDI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

C.ADDI snapshots one complete Reg5 source, sign-extends simm5, adds modulo 2^XLEN, and pushes the result to T.

## Pseudocode (informative)

```c
rd = rs1 + SignExtend(imm12);
```

## Encoding Notes

- `C.ADDI snapshots one complete Reg5 source, sign-extends simm5, adds modulo 2^XLEN, and pushes the result to T.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.addi srcL, simm, ->t` | 16 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
