# C.ADDI

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/arithmetic.md">Arithmetic</a> &nbsp;|&nbsp;
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

[16-bit C.] Instruction from the Arithmetic group.

## Pseudocode (informative)

```c
rd = rs1 + SignExtend(imm12);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.addi srcL, simm, ->t` | 16 | — |

<div class="insn-nav">

← [Arithmetic](../groups/arithmetic.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
