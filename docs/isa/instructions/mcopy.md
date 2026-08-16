# MCOPY

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `MCOPY [RegSrc0, RegSrc1, RegSrc2]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_mcopy.svg" alt="MCOPY encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Copies a non-overlapping byte range in restartable forward memory steps.

## Pseudocode (informative)

```c
// Execute MCOPY as defined by the Bundle Split semantics.
```

## Encoding Notes

- `Copies a non-overlapping byte range in restartable forward memory steps.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `MCOPY [RegSrc0, RegSrc1, RegSrc2]` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
