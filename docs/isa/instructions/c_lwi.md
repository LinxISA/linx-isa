# C.LWI

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/lda_base_imm.md">LDA/BASE_IMM</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.lwi [srcL, simm], ->t`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_lwi.svg" alt="C.LWI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

C.LWI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value.

## Pseudocode (informative)

```c
// Execute C.LWI as defined by the LDA/BASE_IMM semantics.
```

## Encoding Notes

- `C.LWI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.lwi [srcL, simm], ->t` | 16 | — |

<div class="insn-nav">

← [LDA/BASE_IMM](../groups/lda_base_imm.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
