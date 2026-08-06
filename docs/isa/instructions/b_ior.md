# B.IOR

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_input_output.md">Bundle Input & Output</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `B.IOR [RegSrc0, RegSrc1, RegSrc2],[RegDst]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_b_ior.svg" alt="B.IOR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Instruction from the Bundle Input & Output group.

## Pseudocode (informative)

```c
// Execute B.IOR as defined by the Bundle Input & Output semantics.
```

## Encoding Notes

- `Binds encoded scalar inputs and outputs to the current bundle interface.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `B.IOR [RegSrc0, RegSrc1, RegSrc2],[RegDst]` | 32 | — |

<div class="insn-nav">

← [Bundle Input & Output](../groups/bundle_input_output.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
