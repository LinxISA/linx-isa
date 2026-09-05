# B.SUBVIEW

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_range_modifier.md">Bundle Range Modifier</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `B.SUBVIEW SrcSelect, RegSrc, uimm11, SubviewSizeCode`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_b_subview.svg" alt="B.SUBVIEW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Decodes one source-range subview modifier and retains its XLEN-wrapped derived offset in the immediately preceding binder group.

## Pseudocode (informative)

```c
// Execute B.SUBVIEW as defined by the Bundle Range Modifier semantics.
```

## Encoding Notes

- `Decodes one source-range subview modifier and retains its XLEN-wrapped derived offset in the immediately preceding binder group.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `B.SUBVIEW SrcSelect, RegSrc, uimm11, SubviewSizeCode` | 32 | — |

<div class="insn-nav">

← [Bundle Range Modifier](../groups/bundle_range_modifier.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
