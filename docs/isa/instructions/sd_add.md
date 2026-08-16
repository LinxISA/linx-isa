# SD.ADD

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/amo.md">AMO</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `sd.add<.{rl, f, rlf}> [SrcL], SrcR`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_sd_add.svg" alt="SD.ADD encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

SD.ADD atomically replaces the aligned 64-bit memory value with its modular sum with SrcR; it does not publish the old value.

## Pseudocode (informative)

```c
// Execute SD.ADD as defined by the AMO semantics.
```

## Encoding Notes

- `SD.ADD atomically replaces the aligned 64-bit memory value with its modular sum with SrcR; it does not publish the old value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `sd.add<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — |

<div class="insn-nav">

← [AMO](../groups/amo.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
