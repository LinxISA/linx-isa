# C.SEXT.H

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/c_unary.md">C.UNARY</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.sext.h srcL, ->t`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_sext_h.svg" alt="C.SEXT.H encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

C.SEXT.H - Sign-extend or zero-extend the selected scalar subword.

## Pseudocode (informative)

```c
// Execute C.SEXT.H as defined by the C.UNARY semantics.
```

## Encoding Notes

- `C.SEXT.H - Sign-extend or zero-extend the selected scalar subword.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.sext.h srcL, ->t` | 16 | — |

<div class="insn-nav">

← [C.UNARY](../groups/c_unary.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
