# C.SETC.EQ

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/set_commit_argument.md">Set Commit Argument</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.setc.eq srcL, srcR`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_setc_eq.svg" alt="C.SETC.EQ encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[16-bit C.] Sets the block-commit condition.

## Pseudocode (informative)

```c
SetCommitArgument(/* condition */);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.setc.eq srcL, srcR` | 16 | — |

<div class="insn-nav">

← [Set Commit Argument](../groups/set_commit_argument.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
