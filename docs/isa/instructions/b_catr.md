# B.CATR

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/block_control_attribute.md">Block Control Attribute</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-17">Ch 17</span>
&nbsp; <strong>CMD — Command and Control</strong> &nbsp;|&nbsp;
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

Instruction from the Block Control Attribute group.

## Pseudocode (informative)

```c
// Execute B.CATR as defined by the Block Control Attribute semantics.
```

## Encoding Notes

- `v0.56 split of legacy B.CATR/B.DATR control fields.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `B.CATR {trap, atomic, <aq, rl, aqrl>, far, dr}` | 32 | — |

<div class="insn-nav">

← [Block Control Attribute](../groups/block_control_attribute.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
