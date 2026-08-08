# FENTRY

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `FENTRY [RegSrc0 ~ RegSrcn], sp!, uimm`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_fentry.svg" alt="FENTRY encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Atomically validates and creates a frame-template entry state.

## Pseudocode (informative)

```c
// Execute FENTRY as defined by the Bundle Split semantics.
```

## Encoding Notes

- `Atomically validates and creates a frame-template entry state.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `FENTRY [RegSrc0 ~ RegSrcn], sp!, uimm` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
