# BSTART.TEPL

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `BSTART.TEPL Mode, Function, DataType`

## Canonical Semantic Aliases

- `BSTART.VEC TileOp, DataType` is accepted only when `TileOp` is catalogued for VEC.
- `BSTART.SFU TileOp, DataType` is accepted only when `TileOp` is catalogued for SFU.
- `BSTART.TEPL Mode, Function, DataType` remains the raw compatibility spelling.
- Canonical disassembly emits the VEC or SFU alias selected by the Tile operation catalog.

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_bstart_tepl.svg" alt="BSTART.TEPL encoding" width="100%" />
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

- `Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `BSTART.TEPL Mode, Function, DataType` | 32 | — |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
