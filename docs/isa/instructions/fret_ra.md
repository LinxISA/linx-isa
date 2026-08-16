# FRET.RA

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `FRET.RA [RegDst0 ~ RegDstn], sp!, uimm`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_fret_ra.svg" alt="FRET.RA encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Restores a restartable stack frame and returns through the pre-restore architectural return address.

## Pseudocode (informative)

```c
// Execute FRET.RA as defined by the Bundle Split semantics.
```

## Encoding Notes

- `Restores a restartable stack frame and returns through the pre-restore architectural return address.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `FRET.RA [RegDst0 ~ RegDstn], sp!, uimm` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
