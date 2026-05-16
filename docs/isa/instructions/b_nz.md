# B.NZ

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/branch.md">Branch</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `b.nz label`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_b_nz.svg" alt="B.NZ encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Conditional PC-relative branch.

## Pseudocode (informative)

```c
// Execute B.NZ as defined by the Branch semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `b.nz label` | 32 | — |

<div class="insn-nav">

← [Branch](../groups/branch.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
