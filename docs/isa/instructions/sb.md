# SB

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/sta_base_reg.md">STA/BASE_REG</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `sb SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_sb.svg" alt="SB encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

SB snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value.

## Pseudocode (informative)

```c
// Execute SB as defined by the STA/BASE_REG semantics.
```

## Encoding Notes

- `SB snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `sb SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 32 | — |

<div class="insn-nav">

← [STA/BASE_REG](../groups/sta_base_reg.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
