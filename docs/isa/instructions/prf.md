# PRF

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/load_register_offset.md">Load Register Offset</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `prf [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_prf.svg" alt="PRF encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Loads a value from memory into a register.

## Pseudocode (informative)

```c
rd = Load(/* addr */);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `prf [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>]` | 32 | — |

<div class="insn-nav">

← [Load Register Offset](../groups/load_register_offset.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
