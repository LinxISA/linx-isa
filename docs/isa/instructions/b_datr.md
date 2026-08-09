# B.DATR

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_data_attribute.md">Bundle Data Attribute</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `B.DATR {layout, datatype, padvalue_or_byteid, cmode, rmode, sat, canonicalize}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_b_datr.svg" alt="B.DATR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Latches tile layout, data type, padding, conversion, rounding, and saturation attributes.

## Pseudocode (informative)

```c
// Execute B.DATR as defined by the Bundle Data Attribute semantics.
```

## Encoding Notes

- `Latches tile layout, data type, padding, conversion, rounding, and saturation attributes.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `B.DATR {layout, datatype, padvalue_or_byteid, cmode, rmode, sat, canonicalize}` | 32 | — |

<div class="insn-nav">

← [Bundle Data Attribute](../groups/bundle_data_attribute.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
