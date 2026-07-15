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

<figure id="encoding-b_arg_32_374ec956affe">
<img src="../wavedrom/enc_b_arg_32_374ec956affe.svg" alt="B.ARG encoding form b_arg_32_374ec956affe" width="100%" />
<figcaption><code>b_arg_32_374ec956affe</code> — <code>B.ARG NORM.normal</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_arg_32_47e8ac50ac96">
<img src="../wavedrom/enc_b_arg_32_47e8ac50ac96.svg" alt="B.ARG encoding form b_arg_32_47e8ac50ac96" width="100%" />
<figcaption><code>b_arg_32_47e8ac50ac96</code> — <code>B.ARG format</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_arg_32_5c8bfa662370">
<img src="../wavedrom/enc_b_arg_32_5c8bfa662370.svg" alt="B.ARG encoding form b_arg_32_5c8bfa662370" width="100%" />
<figcaption><code>b_arg_32_5c8bfa662370</code> — <code>B.ARG NZ2DN.canon</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_arg_32_95152c29a268">
<img src="../wavedrom/enc_b_arg_32_95152c29a268.svg" alt="B.ARG encoding form b_arg_32_95152c29a268" width="100%" />
<figcaption><code>b_arg_32_95152c29a268</code> — <code>B.ARG ND2ZN.normal, FP16, Null</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_arg_32_c6d5c49a4ad7">
<img src="../wavedrom/enc_b_arg_32_c6d5c49a4ad7.svg" alt="B.ARG encoding form b_arg_32_c6d5c49a4ad7" width="100%" />
<figcaption><code>b_arg_32_c6d5c49a4ad7</code> — <code>B.ARG DN2ZN.normal, FP16, Null</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_arg_32_f19d18f2126b">
<img src="../wavedrom/enc_b_arg_32_f19d18f2126b.svg" alt="B.ARG encoding form b_arg_32_f19d18f2126b" width="100%" />
<figcaption><code>b_arg_32_f19d18f2126b</code> — <code>B.ARG DN2NZ.normal, FP32, Null</code>. MSB is on the left, LSB is on the right.</figcaption>
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

| Form ID | Assembly | Length | Decode | Encoding |
|---------|----------|--------|--------|----------|
| `b_arg_32_374ec956affe` | `B.ARG NORM.normal` | 32 | — | [SVG](../wavedrom/enc_b_arg_32_374ec956affe.svg) |
| `b_arg_32_47e8ac50ac96` | `B.ARG format` | 32 | — | [SVG](../wavedrom/enc_b_arg_32_47e8ac50ac96.svg) |
| `b_arg_32_5c8bfa662370` | `B.ARG NZ2DN.canon` | 32 | — | [SVG](../wavedrom/enc_b_arg_32_5c8bfa662370.svg) |
| `b_arg_32_95152c29a268` | `B.ARG ND2ZN.normal, FP16, Null` | 32 | — | [SVG](../wavedrom/enc_b_arg_32_95152c29a268.svg) |
| `b_arg_32_c6d5c49a4ad7` | `B.ARG DN2ZN.normal, FP16, Null` | 32 | — | [SVG](../wavedrom/enc_b_arg_32_c6d5c49a4ad7.svg) |
| `b_arg_32_f19d18f2126b` | `B.ARG DN2NZ.normal, FP32, Null` | 32 | — | [SVG](../wavedrom/enc_b_arg_32_f19d18f2126b.svg) |

<div class="insn-nav">

← [Block Argument](../groups/block_argument.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
