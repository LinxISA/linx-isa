# LUI

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/immediate.md">Immediate</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `lui simm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_lui.svg" alt="LUI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Load upper immediate. Materializes a 20-bit constant in the upper bits of the destination.

## Pseudocode (informative)

```c
rd = ZeroExtend(imm20) << 12;
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `lui simm, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [Immediate](../groups/immediate.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
