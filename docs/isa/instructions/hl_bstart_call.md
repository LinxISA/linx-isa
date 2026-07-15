# HL.BSTART CALL

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/bstart.md">BSTART</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `HL.BSTART.CALL <br_label>`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_bstart_call.svg" alt="HL.BSTART CALL encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[48-bit HL.] Unconditionally transfers to a call block. The instruction preserves `ra`; returning calls require an adjacent `SETRET` or `C.SETRET`.

## Pseudocode (informative)

```c
// BSTART.CALL preserves ra. Returning source forms place SETRET/C.SETRET adjacent to the header.
EndBlock(); BeginNextBlock(CALL);
```

## Encoding Notes

- `Bare HL.BSTART.CALL preserves ra. A returning call must be preceded by SETRET or C.SETRET with an explicit return label.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `HL.BSTART.CALL <br_label>` | 48 | — |

<div class="insn-nav">

← [BSTART](../groups/bstart.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
