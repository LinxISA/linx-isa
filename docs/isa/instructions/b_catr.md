# B.CATR

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_control_attribute.md">Bundle Control Attribute</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `B.CATR {trap, atomic, <aq, rl, aqrl>, far, dr}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_b_catr.svg" alt="B.CATR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Latches bundle control, trap, atomic, ordering, and address-class attributes.

## Pseudocode (informative)

```c
// Execute B.CATR as defined by the Bundle Control Attribute semantics.
```

## Encoding Notes

- `Latches bundle control, trap, atomic, ordering, and address-class attributes.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `B.CATR {trap, atomic, <aq, rl, aqrl>, far, dr}` | 32 | — |

<div class="insn-nav">

← [Bundle Control Attribute](../groups/bundle_control_attribute.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
