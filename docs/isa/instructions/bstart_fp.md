# BSTART.FP

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `BSTART.FP FALL`
- `BSTART.FP RET`
- `BSTART.FP DIRECT, <label>`
- `BSTART.FP IND`
- `BSTART.FP COND, <label>`

## Encoding

<div class="enc-diagram">

<figure id="encoding-bstart_fp_32_2d6ee1b89bae">
<img src="../wavedrom/enc_bstart_fp_32_2d6ee1b89bae.svg" alt="BSTART.FP encoding form bstart_fp_32_2d6ee1b89bae" width="100%" />
<figcaption><code>bstart_fp_32_2d6ee1b89bae</code> — <code>BSTART.FP FALL</code>. MSB is on the left, LSB is on the right.</figcaption>
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
| `bstart_fp_32_2d6ee1b89bae` | `BSTART.FP FALL` | 32 | — | [SVG](../wavedrom/enc_bstart_fp_32_2d6ee1b89bae.svg) |
| `bstart_fp_32_82106bc72d98` | `BSTART.FP RET` | 32 | — | [SVG](../wavedrom/enc_bstart_fp_32_82106bc72d98.svg) |
| `bstart_fp_32_c6cf502b7ebd` | `BSTART.FP DIRECT, <label>` | 32 | — | [SVG](../wavedrom/enc_bstart_fp_32_c6cf502b7ebd.svg) |
| `bstart_fp_32_dea7bdf4c480` | `BSTART.FP IND` | 32 | — | [SVG](../wavedrom/enc_bstart_fp_32_dea7bdf4c480.svg) |
| `bstart_fp_32_ed54a0ac3b7a` | `BSTART.FP COND, <label>` | 32 | — | [SVG](../wavedrom/enc_bstart_fp_32_ed54a0ac3b7a.svg) |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
