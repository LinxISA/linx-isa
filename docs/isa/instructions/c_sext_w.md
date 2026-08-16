# C.SEXT.W

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.sext.w srcL, ->t`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_sext_w.svg" alt="C.SEXT.W encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

C.SEXT.W sign-extends SrcL[31:0] to XLEN and pushes the result to T.

## Pseudocode (informative)

```c
// Execute C.SEXT.W as defined by the ALU semantics.
```

## Encoding Notes

- `C.SEXT.W sign-extends SrcL[31:0] to XLEN and pushes the result to T.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.sext.w srcL, ->t` | 16 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
