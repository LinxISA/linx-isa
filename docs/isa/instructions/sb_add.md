# SB.ADD

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/amo.md">AMO</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `sb.add<.{rl}> [SrcL], SrcR`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_sb_add.svg" alt="SB.ADD encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

v0.58 32-bit atomic store-op add byte: data=[SrcL]; [SrcL]=data+SrcR. Encoded in the SW slot (14..12=011) with the op5 size-override bit b31 set, shrinking the access from word to byte. Supports rl ordering only and has no far flag.

## Pseudocode (informative)

```c
// Execute SB.ADD as defined by the AMO semantics.
```

## Encoding Notes

- `v0.58 32-bit atomic store-op add byte: data=[SrcL]; [SrcL]=data+SrcR. Encoded in the SW slot (14..12=011) with the op5 size-override bit b31 set, shrinking the access from word to byte. Supports rl ordering only and has no far flag.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `sb.add<.{rl}> [SrcL], SrcR` | 32 | — |

<div class="insn-nav">

← [AMO](../groups/amo.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
