# V.QPUSH

<div class="insn-header">

<span class="badge-64">64-bit V.</span> **Group:** <a href="../groups/general_manager.md">General Manager</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-09">Ch 09</span>
&nbsp; <strong>Memory Operations — Loads, Stores, and Atomics</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `v.qpush SrcL.ud, SrcR.ud, ->Dst`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_v_qpush_parts.svg" alt="V.QPUSH encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[64-bit V.] Instruction from the General Manager group.

## Pseudocode (informative)

```c
// Execute V.QPUSH as defined by the General Manager semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `v.qpush SrcL.ud, SrcR.ud, ->Dst` | 64 | — |

<div class="insn-nav">

← [General Manager](../groups/general_manager.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
