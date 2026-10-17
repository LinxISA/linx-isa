# B.DATR

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_data_attribute.md">Bundle Data Attribute</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-17">Ch 17</span>
&nbsp; <strong>CMD — Command and Control</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `B.DATR {layout, datatype, padvalue_or_byteid, cmode, rmode, sat, canonicalize, predinv, zero}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_b_datr.svg" alt="B.DATR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Latch per-block tile attributes and carrier-independent ExecutionMask controls PredInv and Zero.

## Pseudocode (informative)

```c
// Execute B.DATR as defined by the Bundle Data Attribute semantics.
```

## Encoding Notes

- `Latch per-block tile attributes and carrier-independent ExecutionMask controls PredInv and Zero.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `B.DATR {layout, datatype, padvalue_or_byteid, cmode, rmode, sat, canonicalize, predinv, zero}` | 32 | — |

<div class="insn-nav">

← [Bundle Data Attribute](../groups/bundle_data_attribute.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
