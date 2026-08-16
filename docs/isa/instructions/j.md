# J

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bru.md">BRU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `j label`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_j.svg" alt="J encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Unconditional PC-relative jump to a target label.

## Pseudocode (informative)

```c
// Execute J as defined by the BRU semantics.
```

## Encoding Notes

- `J - Jump to the PC-relative target.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `j label` | 32 | — |

<div class="insn-nav">

← [BRU](../groups/bru.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
