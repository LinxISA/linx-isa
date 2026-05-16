# CMP.LT

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/compare_instruction.md">Compare Instruction</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `cmp.lt SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_cmp_lt.svg" alt="CMP.LT encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Compare less-than (signed).

## Pseudocode (informative)

```c
// Execute CMP.LT as defined by the Compare Instruction semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `cmp.lt SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [Compare Instruction](../groups/compare_instruction.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
