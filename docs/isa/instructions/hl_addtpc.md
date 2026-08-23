# HL.ADDTPC

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/bru.md">BRU</a> &nbsp;|&nbsp;
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

HL.ADDTPC - Add a signed 4 KiB page displacement to the current TPC.

## Pseudocode (informative)

```c
rd = PC + SignExtend(imm);
```

## Encoding Notes

- `HL.ADDTPC - Add a signed 4 KiB page displacement to the current TPC.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.addtpc imm, ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [BRU](../groups/bru.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
