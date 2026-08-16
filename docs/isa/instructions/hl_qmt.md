# HL.QMT

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/general.md">General</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.qmt[.{i,e,s,r,ie,is,ir,es,er,ies,ier}] SrcL[, SrcR when i], ->RegDst`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_qmt.svg" alt="HL.QMT encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Queries, initializes, notifies, suspends, or restores one General Queue Management queue.

## Pseudocode (informative)

```c
// Execute HL.QMT as defined by the General semantics.
```

## Encoding Notes

- `Queries, initializes, notifies, suspends, or restores one General Queue Management queue.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.qmt[.{i,e,s,r,ie,is,ir,es,er,ies,ier}] SrcL[, SrcR when i], ->RegDst` | 48 | — |

<div class="insn-nav">

← [General](../groups/general.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
