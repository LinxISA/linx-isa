# L.BSTART.FP

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bstart.md">BSTART</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `L.BSTART.FP COND, <label>`
- `L.BSTART.FP DIRECT, <label>`
- `L.BSTART.FP CALL, <label>`
- `L.BSTART.FP FALL<, fixup_label>`

## Encoding

<div class="enc-diagram">

<figure id="encoding-l_bstart_fp_64_098e57019d7b">
<img src="../wavedrom/enc_l_bstart_fp_64_098e57019d7b.svg" alt="L.BSTART.FP encoding form l_bstart_fp_64_098e57019d7b" width="100%" />
<figcaption><code>l_bstart_fp_64_098e57019d7b</code> — <code>L.BSTART.FP COND, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-l_bstart_fp_64_0cac9941f7d4">
<img src="../wavedrom/enc_l_bstart_fp_64_0cac9941f7d4.svg" alt="L.BSTART.FP encoding form l_bstart_fp_64_0cac9941f7d4" width="100%" />
<figcaption><code>l_bstart_fp_64_0cac9941f7d4</code> — <code>L.BSTART.FP DIRECT, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-l_bstart_fp_64_2067ad6667ed">
<img src="../wavedrom/enc_l_bstart_fp_64_2067ad6667ed.svg" alt="L.BSTART.FP encoding form l_bstart_fp_64_2067ad6667ed" width="100%" />
<figcaption><code>l_bstart_fp_64_2067ad6667ed</code> — <code>L.BSTART.FP CALL, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-l_bstart_fp_64_8115c042ef26">
<img src="../wavedrom/enc_l_bstart_fp_64_8115c042ef26.svg" alt="L.BSTART.FP encoding form l_bstart_fp_64_8115c042ef26" width="100%" />
<figcaption><code>l_bstart_fp_64_8115c042ef26</code> — <code>L.BSTART.FP FALL<, fixup_label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

</div>

## Description

Instruction from the BSTART group.

## Pseudocode (informative)

```c
// Execute L.BSTART.FP as defined by the BSTART semantics.
```

## Encoding Notes

- `Bare L.BSTART.FP CALL preserves ra. A returning call must be preceded by SETRET or C.SETRET with an explicit return label.`

## Full Catalog Forms

| Form ID | Assembly | Length | Decode | Encoding |
|---------|----------|--------|--------|----------|
| `l_bstart_fp_64_098e57019d7b` | `L.BSTART.FP COND, <label>` | 64 | — | [SVG](../wavedrom/enc_l_bstart_fp_64_098e57019d7b.svg) |
| `l_bstart_fp_64_0cac9941f7d4` | `L.BSTART.FP DIRECT, <label>` | 64 | — | [SVG](../wavedrom/enc_l_bstart_fp_64_0cac9941f7d4.svg) |
| `l_bstart_fp_64_2067ad6667ed` | `L.BSTART.FP CALL, <label>` | 64 | — | [SVG](../wavedrom/enc_l_bstart_fp_64_2067ad6667ed.svg) |
| `l_bstart_fp_64_8115c042ef26` | `L.BSTART.FP FALL<, fixup_label>` | 64 | — | [SVG](../wavedrom/enc_l_bstart_fp_64_8115c042ef26.svg) |

<div class="insn-nav">

← [BSTART](../groups/bstart.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
