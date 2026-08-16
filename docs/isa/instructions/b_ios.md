# B.IOS

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_input_output.md">Bundle Input & Output</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `B.IOS S<SharedTID>, mask=<PE_MASK> | B.IOS mask=<PE_MASK>, ->S<SharedTID><TSize>`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_b_ios.svg" alt="B.IOS encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Binds one ordered absolute Core-private Shared register S0..S255 as a source or destination with a common four-PE participation mask.

## Pseudocode (informative)

```c
// Execute B.IOS as defined by the Bundle Input & Output semantics.
```

## Encoding Notes

- `Binds one ordered absolute Core-private Shared register S0..S255 as a source or destination with a common four-PE participation mask.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `B.IOS S<SharedTID>, mask=<PE_MASK> | B.IOS mask=<PE_MASK>, ->S<SharedTID><TSize>` | 32 | — |

<div class="insn-nav">

← [Bundle Input & Output](../groups/bundle_input_output.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
