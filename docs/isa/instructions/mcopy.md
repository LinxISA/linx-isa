# MCOPY

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
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

Copies an encoded memory range with instruction-atomic preflight and snapshot semantics.

## Pseudocode (informative)

```c
// Execute MCOPY as defined by the Bundle Split semantics.
```

## Encoding Notes

- `Copies an encoded memory range with instruction-atomic preflight and snapshot semantics.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `MCOPY [RegSrc0, RegSrc1, RegSrc2]` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
