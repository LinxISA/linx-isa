# HL.LWUIP

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/lda_pair.md">LDA/PAIR</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.lwuip [SrcL, simm], ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_lwuip.svg" alt="HL.LWUIP encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.LWUIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values.

## Pseudocode (informative)

```c
// Execute HL.LWUIP as defined by the LDA/PAIR semantics.
```

## Encoding Notes

- `HL.LWUIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.lwuip [SrcL, simm], ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [LDA/PAIR](../groups/lda_pair.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
