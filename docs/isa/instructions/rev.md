# REV

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `rev SrcL,  M, N, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_rev.svg" alt="REV encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Bit-reversal operation.

## Pseudocode (informative)

```c
// Execute REV as defined by the ALU semantics.
```

## Encoding Notes

- `REV reverses the bytes of an independently selected wrapping scalar field, zero-fills high result bits, and returns zero for a non-byte width.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `rev SrcL,  M, N, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
