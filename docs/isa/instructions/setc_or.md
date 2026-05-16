# SETC.OR

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/set_commit_argument.md">Set Commit Argument</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `setc.or SrcL, SrcR<.sw, .uw, .not>`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_setc_or.svg" alt="SETC.OR encoding" width="100%" />
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
| `setc.or SrcL, SrcR<.sw, .uw, .not>` | 32 | — |

<div class="insn-nav">

← [Set Commit Argument](../groups/set_commit_argument.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
