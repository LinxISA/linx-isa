# HL.PRFI.UA

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/lda.md">LDA</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.prfi.ua{.l1,.l2,.l3} [SrcL, simm], ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_prfi_ua.svg" alt="HL.PRFI.UA encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.PRFI.UA snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint and publishes the effective address.

## Pseudocode (informative)

```c
// Execute HL.PRFI.UA as defined by the LDA semantics.
```

## Encoding Notes

- `HL.PRFI.UA snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint and publishes the effective address.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.prfi.ua{.l1,.l2,.l3} [SrcL, simm], ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [LDA](../groups/lda.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
