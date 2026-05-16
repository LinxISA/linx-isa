# HL.ADDTPC

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/pc_relative.md">PC-Relative</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.addtpc imm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_addtpc.svg" alt="HL.ADDTPC encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[48-bit HL.] Instruction from the PC-Relative group.

## Pseudocode (informative)

```c
rd = PC + SignExtend(imm);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.addtpc imm, ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [PC-Relative](../groups/pc_relative.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
