# C.EBREAK

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/c_tinst.md">C.TINST</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.break imm`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_ebreak.svg" alt="C.EBREAK encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[16-bit C.] Instruction from the C.TINST group.

## Pseudocode (informative)

```c
Trap(EBREAK);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.break imm` | 16 | — |

<div class="insn-nav">

← [C.TINST](../groups/c_tinst.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
