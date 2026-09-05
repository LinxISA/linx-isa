# BSTART.MSCATTER.INC

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `BSTART.MSCATTER.INC DataType`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_bstart_mscatter_inc.svg" alt="BSTART.MSCATTER.INC encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Terminates the current block and begins the next.

## Pseudocode (informative)

```c
EndBlock(); BeginNextBlock(/* kind */);
```

## Encoding Notes

- `Starts GM indexed mscatter.inc operation.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `BSTART.MSCATTER.INC DataType` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
