# HL.BFI

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.bfi SrcL, SrcR, M, N, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_bfi.svg" alt="HL.BFI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[48-bit HL.] Bit-field insert.

## Pseudocode (informative)

```c
// Execute HL.BFI as defined by the ALU semantics.
```

## Encoding Notes

- `HL.BFI inserts ascending low source bits into an inclusive wrapping destination interval of a snapshotted base value and publishes the XLEN result.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.bfi SrcL, SrcR, M, N, ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
