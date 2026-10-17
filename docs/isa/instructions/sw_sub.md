# SW.SUB

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/amo.md">AMO</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `sw.sub<.{rl}> [SrcL], SrcR`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_sw_sub.svg" alt="SW.SUB encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

v0.58 32-bit atomic store-op subtract word: data=[SrcL]; [SrcL]=data-SrcR. Uses op5 0_1000: b31=0 keeps the word/doubleword width and b30..27=1000 selects SUB. Supports rl ordering only and has no far flag.

## Pseudocode (informative)

```c
// Execute SW.SUB as defined by the AMO semantics.
```

## Encoding Notes

- `v0.58 32-bit atomic store-op subtract word: data=[SrcL]; [SrcL]=data-SrcR. Uses op5 0_1000: b31=0 keeps the word/doubleword width and b30..27=1000 selects SUB. Supports rl ordering only and has no far flag.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `sw.sub<.{rl}> [SrcL], SrcR` | 32 | — |

<div class="insn-nav">

← [AMO](../groups/amo.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
