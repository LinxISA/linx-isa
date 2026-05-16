# BSTART.FP

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/block_split.md">Block Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `BSTART.FP RET`
- `BSTART.FP IND`
- `BSTART.FP COND, <label>`
- `BSTART.FP DIRECT, <label>`
- `BSTART.FP ICALL`
- `BSTART.FP CALL, <label>`
- `BSTART.FP FALL<, fixup_label>`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_bstart_fp.svg" alt="BSTART.FP encoding" width="100%" />
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
| `BSTART.FP RET` | 32 | — |
| `BSTART.FP IND` | 32 | — |
| `BSTART.FP COND, <label>` | 32 | — |
| `BSTART.FP DIRECT, <label>` | 32 | — |
| `BSTART.FP ICALL` | 32 | — |
| `BSTART.FP CALL, <label>` | 32 | — |
| `BSTART.FP FALL<, fixup_label>` | 32 | — |

<div class="insn-nav">

← [Block Split](../groups/block_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
