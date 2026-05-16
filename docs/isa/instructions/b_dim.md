# B.DIM

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/block_argument.md">Block Argument</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `B.DIM RegSrc, uimm, ->LB2`
- `B.DIM RegSrc, uimm, ->LB0`
- `B.DIM RegSrc, uimm, ->LB1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_b_dim.svg" alt="B.DIM encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Instruction from the Block Argument group.

## Pseudocode (informative)

```c
// Execute B.DIM as defined by the Block Argument semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `B.DIM RegSrc, uimm, ->LB2` | 32 | — |
| `B.DIM RegSrc, uimm, ->LB0` | 32 | — |
| `B.DIM RegSrc, uimm, ->LB1` | 32 | — |

<div class="insn-nav">

← [Block Argument](../groups/block_argument.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
