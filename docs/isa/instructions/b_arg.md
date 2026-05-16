# B.ARG

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/block_argument.md">Block Argument</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `B.ARG NORM.normal`
- `B.ARG format`
- `B.ARG NZ2DN.canon`
- `B.ARG ND2ZN.normal, FP16, Null`
- `B.ARG DN2ZN.normal, FP16, Null`
- `B.ARG DN2NZ.normal, FP32, Null`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_b_arg.svg" alt="B.ARG encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Instruction from the Block Argument group.

## Pseudocode (informative)

```c
// Execute B.ARG as defined by the Block Argument semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `B.ARG NORM.normal` | 32 | — |
| `B.ARG format` | 32 | — |
| `B.ARG NZ2DN.canon` | 32 | — |
| `B.ARG ND2ZN.normal, FP16, Null` | 32 | — |
| `B.ARG DN2ZN.normal, FP16, Null` | 32 | — |
| `B.ARG DN2NZ.normal, FP32, Null` | 32 | — |

<div class="insn-nav">

← [Block Argument](../groups/block_argument.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
