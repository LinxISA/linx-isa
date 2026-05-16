# HL.CCAT

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/concat.md">Concat</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-18">Ch 18</span>
&nbsp; <strong>RSV — Reserved and Indexed Operations</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.ccat SrcL, SrcR, shamt, ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_ccat.svg" alt="HL.CCAT encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[48-bit HL.] Instruction from the Concat group.

## Pseudocode (informative)

```c
// Execute HL.CCAT as defined by the Concat semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.ccat SrcL, SrcR, shamt, ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [Concat](../groups/concat.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
