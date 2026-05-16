# C.LWI

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/load_immediate_offset.md">Load Immediate Offset</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.lwi [srcL, simm], ->t`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_lwi.svg" alt="C.LWI encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[16-bit C.] Loads a value from memory into a register.

## Pseudocode (informative)

```c
rd = Load(/* addr */);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.lwi [srcL, simm], ->t` | 16 | — |

<div class="insn-nav">

← [Load Immediate Offset](../groups/load_immediate_offset.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
