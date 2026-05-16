# EBREAK

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/execution_control.md">Execution Control</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `ebreak imm`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_ebreak.svg" alt="EBREAK encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Environment break instruction. Traps to the debugging or OS handler.

## Pseudocode (informative)

```c
Trap(EBREAK);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `ebreak imm` | 32 | — |

<div class="insn-nav">

← [Execution Control](../groups/execution_control.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
