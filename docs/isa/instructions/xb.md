# XB

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `XB ACR-ID, C-ID`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_xb.svg" alt="XB encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Inventories an extension-owned cross-block transfer encoding that PTO rejects before field interpretation or architectural effects.

## Pseudocode (informative)

```c
// Execute XB as defined by the Bundle Split semantics.
```

## Encoding Notes

- `Inventories an extension-owned cross-block transfer encoding that PTO rejects before field interpretation or architectural effects.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `XB ACR-ID, C-ID` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
