# BSTART.FP

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `BSTART.FP FALL<, fixup_label>`
- `BSTART.FP ICALL`
- `BSTART.FP RET`
- `BSTART.FP DIRECT, <label>`
- `BSTART.FP IND`
- `BSTART.FP CALL, <label>`
- `BSTART.FP COND, <label>`

## Encoding

<div class="enc-diagram">

<figure id="encoding-bstart_fp_32_494fe06e4fb2">
<img src="../wavedrom/enc_bstart_fp_32_494fe06e4fb2.svg" alt="BSTART.FP encoding form bstart_fp_32_494fe06e4fb2" width="100%" />
<figcaption><code>bstart_fp_32_494fe06e4fb2</code> — <code>BSTART.FP FALL<, fixup_label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-bstart_fp_32_69538a87dfb1">
<img src="../wavedrom/enc_bstart_fp_32_69538a87dfb1.svg" alt="BSTART.FP encoding form bstart_fp_32_69538a87dfb1" width="100%" />
<figcaption><code>bstart_fp_32_69538a87dfb1</code> — <code>BSTART.FP ICALL</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-bstart_fp_32_82106bc72d98">
<img src="../wavedrom/enc_bstart_fp_32_82106bc72d98.svg" alt="BSTART.FP encoding form bstart_fp_32_82106bc72d98" width="100%" />
<figcaption><code>bstart_fp_32_82106bc72d98</code> — <code>BSTART.FP RET</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-bstart_fp_32_c6cf502b7ebd">
<img src="../wavedrom/enc_bstart_fp_32_c6cf502b7ebd.svg" alt="BSTART.FP encoding form bstart_fp_32_c6cf502b7ebd" width="100%" />
<figcaption><code>bstart_fp_32_c6cf502b7ebd</code> — <code>BSTART.FP DIRECT, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-bstart_fp_32_dea7bdf4c480">
<img src="../wavedrom/enc_bstart_fp_32_dea7bdf4c480.svg" alt="BSTART.FP encoding form bstart_fp_32_dea7bdf4c480" width="100%" />
<figcaption><code>bstart_fp_32_dea7bdf4c480</code> — <code>BSTART.FP IND</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-bstart_fp_32_eb33ff25b92a">
<img src="../wavedrom/enc_bstart_fp_32_eb33ff25b92a.svg" alt="BSTART.FP encoding form bstart_fp_32_eb33ff25b92a" width="100%" />
<figcaption><code>bstart_fp_32_eb33ff25b92a</code> — <code>BSTART.FP CALL, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-bstart_fp_32_ed54a0ac3b7a">
<img src="../wavedrom/enc_bstart_fp_32_ed54a0ac3b7a.svg" alt="BSTART.FP encoding form bstart_fp_32_ed54a0ac3b7a" width="100%" />
<figcaption><code>bstart_fp_32_ed54a0ac3b7a</code> — <code>BSTART.FP COND, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
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

| Form ID | Assembly | Length | Decode | Encoding |
|---------|----------|--------|--------|----------|
| `bstart_fp_32_494fe06e4fb2` | `BSTART.FP FALL<, fixup_label>` | 32 | — | [SVG](../wavedrom/enc_bstart_fp_32_494fe06e4fb2.svg) |
| `bstart_fp_32_69538a87dfb1` | `BSTART.FP ICALL` | 32 | — | [SVG](../wavedrom/enc_bstart_fp_32_69538a87dfb1.svg) |
| `bstart_fp_32_82106bc72d98` | `BSTART.FP RET` | 32 | — | [SVG](../wavedrom/enc_bstart_fp_32_82106bc72d98.svg) |
| `bstart_fp_32_c6cf502b7ebd` | `BSTART.FP DIRECT, <label>` | 32 | — | [SVG](../wavedrom/enc_bstart_fp_32_c6cf502b7ebd.svg) |
| `bstart_fp_32_dea7bdf4c480` | `BSTART.FP IND` | 32 | — | [SVG](../wavedrom/enc_bstart_fp_32_dea7bdf4c480.svg) |
| `bstart_fp_32_eb33ff25b92a` | `BSTART.FP CALL, <label>` | 32 | — | [SVG](../wavedrom/enc_bstart_fp_32_eb33ff25b92a.svg) |
| `bstart_fp_32_ed54a0ac3b7a` | `BSTART.FP COND, <label>` | 32 | — | [SVG](../wavedrom/enc_bstart_fp_32_ed54a0ac3b7a.svg) |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
