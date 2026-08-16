# B.Z

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bru.md">BRU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `b.z label`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_b_z.svg" alt="B.Z encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

B.Z - Conditionally branch to the PC-relative target after comparing scalar operands.

## Pseudocode (informative)

```c
// Execute B.Z as defined by the BRU semantics.
```

## Encoding Notes

- `B.Z - Conditionally branch to the PC-relative target after comparing scalar operands.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `b.z label` | 32 | — |

<div class="insn-nav">

← [BRU](../groups/bru.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
