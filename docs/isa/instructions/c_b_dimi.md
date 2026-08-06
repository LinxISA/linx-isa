# C.B.DIMI

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/bundle_dimension.md">Bundle Dimension</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `C.B.DIMI imm, ->{LB0, LB1, LB2}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_b_dimi.svg" alt="C.B.DIMI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[16-bit C.] Instruction from the Bundle Dimension group.

## Pseudocode (informative)

```c
// Execute C.B.DIMI as defined by the Bundle Dimension semantics.
```

## Encoding Notes

- `Writes one of the three bundle-local dimension registers.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `C.B.DIMI imm, ->{LB0, LB1, LB2}` | 16 | — |

<div class="insn-nav">

← [Bundle Dimension](../groups/bundle_dimension.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
