# ADDTPC

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bru.md">BRU</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `addtpc simm, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_addtpc.svg" alt="ADDTPC encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

PC-relative addition. Adds an immediate to the current PC/TPC and writes the result.

## Pseudocode (informative)

```c
rd = PC + SignExtend(imm);
```

## Encoding Notes

- `ADDTPC - Add the encoded displacement to the program counter.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `addtpc simm, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [BRU](../groups/bru.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
