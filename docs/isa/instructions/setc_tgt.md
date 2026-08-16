# SETC.TGT

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/sys.md">SYS</a> &nbsp;|&nbsp;
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

- `SETC.TGT snapshots SrcL into BARG.BPCN for the active Standard or Floating block.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `setc.tgt SrcL` | 32 | — |

<div class="insn-nav">

← [SYS](../groups/sys.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
