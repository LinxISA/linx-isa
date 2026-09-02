# SH.U

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/sta_base_reg.md">STA/BASE_REG</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `sh.u SrcD, [SrcL, SrcR<{.sw,.uw}>]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_sh_u.svg" alt="SH.U encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

SH.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value.

## Pseudocode (informative)

```c
// Execute SH.U as defined by the STA/BASE_REG semantics.
```

## Encoding Notes

- `SH.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `sh.u SrcD, [SrcL, SrcR<{.sw,.uw}>]` | 32 | — |

<div class="insn-nav">

← [STA/BASE_REG](../groups/sta_base_reg.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
