# FRET.STK

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `FRET.STK [ra ~ RegDstn], sp!, uimm`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_fret_stk.svg" alt="FRET.STK encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Restores a restartable stack frame whose first stack slot supplies the validated return target.

## Pseudocode (informative)

```c
// Execute FRET.STK as defined by the Bundle Split semantics.
```

## Encoding Notes

- `Restores a restartable stack frame whose first stack slot supplies the validated return target.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `FRET.STK [ra ~ RegDstn], sp!, uimm` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
