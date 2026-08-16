# SW.SMIN

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/amo.md">AMO</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `sw.smin<.{rl, f, rlf}> [SrcL], SrcR`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_sw_smin.svg" alt="SW.SMIN encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

SW.SMIN atomically replaces the aligned 32-bit memory value with its signed minimum with SrcR; it does not publish the old value.

## Pseudocode (informative)

```c
// Execute SW.SMIN as defined by the AMO semantics.
```

## Encoding Notes

- `SW.SMIN atomically replaces the aligned 32-bit memory value with its signed minimum with SrcR; it does not publish the old value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `sw.smin<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — |

<div class="insn-nav">

← [AMO](../groups/amo.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
