# C.SETRET

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/move.md">Move</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.setret uimm, - >Ra`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_setret.svg" alt="C.SETRET encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[16-bit C.] Instruction from the Move group.

## Pseudocode (informative)

```c
ra = PC + ZeroExtend(imm << 1);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.setret uimm, - >Ra` | 16 | — |

<div class="insn-nav">

← [Move](../groups/move.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
