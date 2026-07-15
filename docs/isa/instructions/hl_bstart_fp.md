# HL.BSTART.FP

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/bstart.md">BSTART</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `HL.BSTART.FP COND, <label>`
- `HL.BSTART.FP FALL<, fixup_label>`
- `HL.BSTART.FP CALL, <label>`
- `HL.BSTART.FP DIRECT, <label>`

## Encoding

<div class="enc-diagram">

<figure id="encoding-hl_bstart_fp_48_038e2e96cf64">
<img src="../wavedrom/enc_hl_bstart_fp_48_038e2e96cf64.svg" alt="HL.BSTART.FP encoding form hl_bstart_fp_48_038e2e96cf64" width="100%" />
<figcaption><code>hl_bstart_fp_48_038e2e96cf64</code> — <code>HL.BSTART.FP COND, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-hl_bstart_fp_48_43530d2ebfae">
<img src="../wavedrom/enc_hl_bstart_fp_48_43530d2ebfae.svg" alt="HL.BSTART.FP encoding form hl_bstart_fp_48_43530d2ebfae" width="100%" />
<figcaption><code>hl_bstart_fp_48_43530d2ebfae</code> — <code>HL.BSTART.FP FALL<, fixup_label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-hl_bstart_fp_48_81b457553844">
<img src="../wavedrom/enc_hl_bstart_fp_48_81b457553844.svg" alt="HL.BSTART.FP encoding form hl_bstart_fp_48_81b457553844" width="100%" />
<figcaption><code>hl_bstart_fp_48_81b457553844</code> — <code>HL.BSTART.FP CALL, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-hl_bstart_fp_48_eb938e9200eb">
<img src="../wavedrom/enc_hl_bstart_fp_48_eb938e9200eb.svg" alt="HL.BSTART.FP encoding form hl_bstart_fp_48_eb938e9200eb" width="100%" />
<figcaption><code>hl_bstart_fp_48_eb938e9200eb</code> — <code>HL.BSTART.FP DIRECT, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

</div>

## Description

[48-bit HL.] Terminates the current block and begins the next.

## Pseudocode (informative)

```c
EndBlock(); BeginNextBlock(/* kind */);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Form ID | Assembly | Length | Decode | Encoding |
|---------|----------|--------|--------|----------|
| `hl_bstart_fp_48_038e2e96cf64` | `HL.BSTART.FP COND, <label>` | 48 | — | [SVG](../wavedrom/enc_hl_bstart_fp_48_038e2e96cf64.svg) |
| `hl_bstart_fp_48_43530d2ebfae` | `HL.BSTART.FP FALL<, fixup_label>` | 48 | — | [SVG](../wavedrom/enc_hl_bstart_fp_48_43530d2ebfae.svg) |
| `hl_bstart_fp_48_81b457553844` | `HL.BSTART.FP CALL, <label>` | 48 | — | [SVG](../wavedrom/enc_hl_bstart_fp_48_81b457553844.svg) |
| `hl_bstart_fp_48_eb938e9200eb` | `HL.BSTART.FP DIRECT, <label>` | 48 | — | [SVG](../wavedrom/enc_hl_bstart_fp_48_eb938e9200eb.svg) |

<div class="insn-nav">

← [BSTART](../groups/bstart.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
