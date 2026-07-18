# CASH

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/atomic_operation.md">Atomic Operation</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `cash<.{aq, rl, aqrl}> [SrcL], SrcR, SrcD, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_cash.svg" alt="CASH encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Atomic memory read-modify-write operation.

## Pseudocode (informative)

```c
// Execute CASH as defined by the Atomic Operation semantics.
```

## Encoding Notes

- `v0.57 32-bit compare-and-swap halfword: old=[SrcL]; if old==SrcR then [SrcL]=SrcD; RegDst=old. Supports aq/rl ordering and has no far flag.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `cash<.{aq, rl, aqrl}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [Atomic Operation](../groups/atomic_operation.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
