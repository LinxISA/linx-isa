# MSET

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `MSET [RegSrc0=Destination, RegSrc1=FillByte, RegSrc2=LengthBytes]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_mset.svg" alt="MSET encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Fills a complete unsigned XLEN byte range with the low byte of an absolute GPR after complete access preflight.

## Pseudocode (informative)

```c
// Execute MSET as defined by the Bundle Split semantics.
```

## Encoding Notes

- `Fills a complete unsigned XLEN byte range with the low byte of an absolute GPR after complete access preflight.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `MSET [RegSrc0=Destination, RegSrc1=FillByte, RegSrc2=LengthBytes]` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
