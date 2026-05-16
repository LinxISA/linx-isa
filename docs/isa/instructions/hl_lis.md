# HL.LIS

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/long_immediate.md">Long Immediate</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.lis simm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_lis.svg" alt="HL.LIS encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[48-bit HL.] Instruction from the Long Immediate group.

## Pseudocode (informative)

```c
// Execute HL.LIS as defined by the Long Immediate semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.lis simm, ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [Long Immediate](../groups/long_immediate.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
