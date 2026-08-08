# ERCOV

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `ERCOV [RegSrc0=BasePtr, RegSrc1=LenBytes, RegSrc2=Kind]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_ercov.svg" alt="ERCOV encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Recovers the encoded execution-context range from memory.

## Pseudocode (informative)

```c
// Execute ERCOV as defined by the Bundle Split semantics.
```

## Encoding Notes

- `Recovers the encoded execution-context range from memory.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `ERCOV [RegSrc0=BasePtr, RegSrc1=LenBytes, RegSrc2=Kind]` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
