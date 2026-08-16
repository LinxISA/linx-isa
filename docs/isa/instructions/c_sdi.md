# C.SDI

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/sta_base_imm.md">STA/BASE_IMM</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.sdi t#1, [srcL, simm]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_sdi.svg" alt="C.SDI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

C.SDI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value.

## Pseudocode (informative)

```c
// Execute C.SDI as defined by the STA/BASE_IMM semantics.
```

## Encoding Notes

- `C.SDI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.sdi t#1, [srcL, simm]` | 16 | — |

<div class="insn-nav">

← [STA/BASE_IMM](../groups/sta_base_imm.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
