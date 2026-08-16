# ASSERT

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/sys.md">SYS</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `assert SrcL`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_assert.svg" alt="ASSERT encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Architectural assertion. Traps if the condition register is zero.

## Pseudocode (informative)

```c
Trap(EBREAK);
```

## Encoding Notes

- `ASSERT raises the architecture assertion trap exactly when its snapshotted scalar condition is zero.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `assert SrcL` | 32 | — |

<div class="insn-nav">

← [SYS](../groups/sys.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
