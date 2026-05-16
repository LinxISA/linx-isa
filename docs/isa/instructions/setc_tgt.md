# SETC.TGT

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/ssr_access.md">SSR Access</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `setc.tgt SrcL`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_setc_tgt.svg" alt="SETC.TGT encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Sets the block-commit condition.

## Pseudocode (informative)

```c
SetCommitArgument(/* condition */);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `setc.tgt SrcL` | 32 | — |

<div class="insn-nav">

← [SSR Access](../groups/ssr_access.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
