# BSTART.TSTORE

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `BSTART.TSTORE DataType`

## Encoding

<div class="enc-diagram">

<figure id="encoding-bstart_tstore_32_6bed4bf0e415">
<img src="../wavedrom/enc_bstart_tstore_32_6bed4bf0e415.svg" alt="BSTART.TSTORE encoding form bstart_tstore_32_6bed4bf0e415" width="100%" />
<figcaption><code>bstart_tstore_32_6bed4bf0e415</code> — <code>BSTART.TSTORE DataType</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-bstart_tstore_32_d592de9e15a8">
<img src="../wavedrom/enc_bstart_tstore_32_d592de9e15a8.svg" alt="BSTART.TSTORE encoding form bstart_tstore_32_d592de9e15a8" width="100%" />
<figcaption><code>bstart_tstore_32_d592de9e15a8</code> — <code>BSTART.TSTORE DataType</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

</div>

## Description

Stores a register value to memory.

## Pseudocode (informative)

```c
EndBlock(); BeginNextBlock(/* kind */);
```

## Encoding Notes

- `Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind.`

## Full Catalog Forms

| Form ID | Assembly | Length | Decode | Encoding |
|---------|----------|--------|--------|----------|
| `bstart_tstore_32_6bed4bf0e415` | `BSTART.TSTORE DataType` | 32 | — | [SVG](../wavedrom/enc_bstart_tstore_32_6bed4bf0e415.svg) |
| `bstart_tstore_32_d592de9e15a8` | `BSTART.TSTORE DataType` | 32 | — | [SVG](../wavedrom/enc_bstart_tstore_32_d592de9e15a8.svg) |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
