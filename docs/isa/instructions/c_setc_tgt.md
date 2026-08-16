# C.SETC.TGT

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.setc.tgt srcL`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_setc_tgt.svg" alt="C.SETC.TGT encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[16-bit C.] Sets the block-commit condition.

## Pseudocode (informative)

```c
SetCommitArgument(/* condition */);
```

## Encoding Notes

- `Snapshot one scalar source value into the active block BARG.BPCN.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.setc.tgt srcL` | 16 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
