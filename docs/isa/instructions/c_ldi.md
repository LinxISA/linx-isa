# C.LDI

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/lda_base_imm.md">LDA/BASE_IMM</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.ldi [srcL, simm], ->t`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_ldi.svg" alt="C.LDI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

C.LDI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value.

## Pseudocode (informative)

```c
// Execute C.LDI as defined by the LDA/BASE_IMM semantics.
```

## Encoding Notes

- `C.LDI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.ldi [srcL, simm], ->t` | 16 | — |

<div class="insn-nav">

← [LDA/BASE_IMM](../groups/lda_base_imm.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
