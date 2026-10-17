# MCOPY.DL

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `MCOPY.DL [RegSrc0, RegSrc1, RegSrc2], ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_mcopy_dl.svg" alt="MCOPY.DL encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

v0.58 32-bit block memory-copy variant in Load mode (D + S/L=Load): copies RegSrc2 bytes from the source address in RegSrc1 to the destination address in RegSrc0 and writes the resulting L2SPM replica address to RegDst; the response is withheld until the copy completes. Distinguished from MCOPY by 26..25=11 and the RegDst field.

## Pseudocode (informative)

```c
// Execute MCOPY.DL as defined by the Bundle Split semantics.
```

## Encoding Notes

- `v0.58 32-bit block memory-copy variant in Load mode (D + S/L=Load): copies RegSrc2 bytes from the source address in RegSrc1 to the destination address in RegSrc0 and writes the resulting L2SPM replica address to RegDst; the response is withheld until the copy completes. Distinguished from MCOPY by 26..25=11 and the RegDst field.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `MCOPY.DL [RegSrc0, RegSrc1, RegSrc2], ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
