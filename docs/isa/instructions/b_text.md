# B.TEXT

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_offset.md">Bundle Offset</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `B.TEXT <label>`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_b_text.svg" alt="B.TEXT encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Sets the out-of-line body entry address for a decoupled bundle.

## Pseudocode (informative)

```c
// Execute B.TEXT as defined by the Bundle Offset semantics.
```

## Encoding Notes

- `Sets the out-of-line body entry address for a decoupled bundle.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `B.TEXT <label>` | 32 | — |

<div class="insn-nav">

← [Bundle Offset](../groups/bundle_offset.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
