# BSTART.STD

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/block_split.md">Block Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `BSTART.STD COND, <label>`
- `BSTART.STD RET`
- `BSTART.STD FALL<, fixup_label>`
- `BSTART.STD ICALL`
- `BSTART.STD CALL, <label>`
- `BSTART.STD IND`
- `BSTART.STD DIRECT, <label>`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_bstart_std.svg" alt="BSTART.STD encoding" width="100%" />
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

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `BSTART.STD COND, <label>` | 32 | — |
| `BSTART.STD RET` | 32 | — |
| `BSTART.STD FALL<, fixup_label>` | 32 | — |
| `BSTART.STD ICALL` | 32 | — |
| `BSTART.STD CALL, <label>` | 32 | — |
| `BSTART.STD IND` | 32 | — |
| `BSTART.STD DIRECT, <label>` | 32 | — |

<div class="insn-nav">

← [Block Split](../groups/block_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
