# HL.DIVU

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/alu.md">ALU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.divu SrcL, SrcR, ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_divu.svg" alt="HL.DIVU encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[48-bit HL.] Unsigned integer division.

## Pseudocode (informative)

```c
rd = (rs2 != 0) ? UnsignedDiv(rs1, rs2) : 0;
```

## Encoding Notes

- `HL.DIVU computes a unsigned XLEN quotient/remainder pair from source snapshots, then publishes quotient followed by remainder.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.divu SrcL, SrcR, ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [ALU](../groups/alu.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
