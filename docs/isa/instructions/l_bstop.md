# L.BSTOP

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `L.BSTOP`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_l_bstop_parts.svg" alt="L.BSTOP encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Commits the current bundle and transfers to its selected continuation.

## Pseudocode (informative)

```c
// Execute L.BSTOP as defined by the Bundle Split semantics.
```

## Encoding Notes

- `Commits the current bundle and transfers to its selected continuation.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `L.BSTOP` | 64 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
