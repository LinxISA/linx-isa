# HL.MIADD

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/reserve.md">RESERVE</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-18">Ch 18</span>
&nbsp; <strong>RSV — Reserved and Indexed Operations</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.miadd SrcL, SrcR, uimm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_miadd.svg" alt="HL.MIADD encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[48-bit HL.] Instruction from the RESERVE group.

## Pseudocode (informative)

```c
// Execute HL.MIADD as defined by the RESERVE semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.miadd SrcL, SrcR, uimm, ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [RESERVE](../groups/reserve.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
