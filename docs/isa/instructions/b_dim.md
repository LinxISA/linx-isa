# B.DIM

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_argument.md">Bundle Argument</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `B.DIM RegSrc, uimm, ->LB1`
- `B.DIM RegSrc, uimm, ->LB0`
- `B.DIM RegSrc, uimm, ->LB2`

## Encoding

<div class="enc-diagram">

<figure id="encoding-b_dim_32_570ae2178c51">
<img src="../wavedrom/enc_b_dim_32_570ae2178c51.svg" alt="B.DIM encoding form b_dim_32_570ae2178c51" width="100%" />
<figcaption><code>b_dim_32_570ae2178c51</code> — <code>B.DIM RegSrc, uimm, ->LB1</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_dim_32_a097166c338b">
<img src="../wavedrom/enc_b_dim_32_a097166c338b.svg" alt="B.DIM encoding form b_dim_32_a097166c338b" width="100%" />
<figcaption><code>b_dim_32_a097166c338b</code> — <code>B.DIM RegSrc, uimm, ->LB0</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_dim_32_f88715bdc6ea">
<img src="../wavedrom/enc_b_dim_32_f88715bdc6ea.svg" alt="B.DIM encoding form b_dim_32_f88715bdc6ea" width="100%" />
<figcaption><code>b_dim_32_f88715bdc6ea</code> — <code>B.DIM RegSrc, uimm, ->LB2</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

</div>

## Description

Writes one of the three bundle-local dimension registers.

## Pseudocode (informative)

```c
// Execute B.DIM as defined by the Bundle Argument semantics.
```

## Encoding Notes

- `Writes one of the three bundle-local dimension registers.`

## Full Catalog Forms

| Form ID | Assembly | Length | Decode | Encoding |
|---------|----------|--------|--------|----------|
| `b_dim_32_570ae2178c51` | `B.DIM RegSrc, uimm, ->LB1` | 32 | — | [SVG](../wavedrom/enc_b_dim_32_570ae2178c51.svg) |
| `b_dim_32_a097166c338b` | `B.DIM RegSrc, uimm, ->LB0` | 32 | — | [SVG](../wavedrom/enc_b_dim_32_a097166c338b.svg) |
| `b_dim_32_f88715bdc6ea` | `B.DIM RegSrc, uimm, ->LB2` | 32 | — | [SVG](../wavedrom/enc_b_dim_32_f88715bdc6ea.svg) |

<div class="insn-nav">

← [Bundle Argument](../groups/bundle_argument.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
