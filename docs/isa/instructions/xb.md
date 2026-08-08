# XB

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
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

Transfers the named context value to a target virtual core block.

## Pseudocode (informative)

```c
// Execute XB as defined by the Bundle Split semantics.
```

## Encoding Notes

- `Transfers the named context value to a target virtual core block.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `XB ACR-ID, C-ID` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
