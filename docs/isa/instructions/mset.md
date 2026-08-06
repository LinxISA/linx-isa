# MSET

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `MSET [RegSrc0, RegSrc1, RegSrc2]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_mset.svg" alt="MSET encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Instruction from the Bundle Split group.

## Pseudocode (informative)

```c
// Execute MSET as defined by the Bundle Split semantics.
```

## Encoding Notes

- `Fills an encoded memory range after complete access preflight.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `MSET [RegSrc0, RegSrc1, RegSrc2]` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
