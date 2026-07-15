# BSTART CALL

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bstart.md">BSTART</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `BSTART.CALL <br_label>`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_bstart_call.svg" alt="BSTART CALL encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Unconditionally transfers to a call block. The instruction preserves `ra`; returning calls require an adjacent `SETRET` or `C.SETRET`.

## Pseudocode (informative)

```c
// BSTART.CALL preserves ra. Returning source forms place SETRET/C.SETRET adjacent to the header.
EndBlock(); BeginNextBlock(CALL);
```

## Encoding Notes

- `Bare BSTART.CALL preserves ra. A returning call must be preceded by SETRET or C.SETRET with an explicit return label.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `BSTART.CALL <br_label>` | 32 | — |

<div class="insn-nav">

← [BSTART](../groups/bstart.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
