# V.LD.MIN

<div class="insn-header">

<span class="badge-64">64-bit V.</span> **Group:** <a href="../groups/atomic_operation.md">Atomic Operation</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `v.ld.min<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_v_ld_min_parts.svg" alt="V.LD.MIN encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[64-bit V.] Atomic memory read-modify-write operation.

## Pseudocode (informative)

```c
// Execute V.LD.MIN as defined by the Atomic Operation semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `v.ld.min<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — |

<div class="insn-nav">

← [Atomic Operation](../groups/atomic_operation.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
