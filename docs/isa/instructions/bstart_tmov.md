# BSTART.TMOV

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `BSTART.TMOV DataType`

## Encoding

<div class="enc-diagram">

<figure id="encoding-bstart_tmov_32_3079328b98d6">
<img src="../wavedrom/enc_bstart_tmov_32_3079328b98d6.svg" alt="BSTART.TMOV encoding form bstart_tmov_32_3079328b98d6" width="100%" />
<figcaption><code>bstart_tmov_32_3079328b98d6</code> — <code>BSTART.TMOV DataType</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-bstart_tmov_32_34d0ab432974">
<img src="../wavedrom/enc_bstart_tmov_32_34d0ab432974.svg" alt="BSTART.TMOV encoding form bstart_tmov_32_34d0ab432974" width="100%" />
<figcaption><code>bstart_tmov_32_34d0ab432974</code> — <code>BSTART.TMOV DataType</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-bstart_tmov_32_472804576301">
<img src="../wavedrom/enc_bstart_tmov_32_472804576301.svg" alt="BSTART.TMOV encoding form bstart_tmov_32_472804576301" width="100%" />
<figcaption><code>bstart_tmov_32_472804576301</code> — <code>BSTART.TMOV DataType</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-bstart_tmov_32_d96181e99f01">
<img src="../wavedrom/enc_bstart_tmov_32_d96181e99f01.svg" alt="BSTART.TMOV encoding form bstart_tmov_32_d96181e99f01" width="100%" />
<figcaption><code>bstart_tmov_32_d96181e99f01</code> — <code>BSTART.TMOV DataType</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-bstart_tmov_32_efe5c49fcb78">
<img src="../wavedrom/enc_bstart_tmov_32_efe5c49fcb78.svg" alt="BSTART.TMOV encoding form bstart_tmov_32_efe5c49fcb78" width="100%" />
<figcaption><code>bstart_tmov_32_efe5c49fcb78</code> — <code>BSTART.TMOV DataType</code>. MSB is on the left, LSB is on the right.</figcaption>
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
| `bstart_tmov_32_3079328b98d6` | `BSTART.TMOV DataType` | 32 | — | [SVG](../wavedrom/enc_bstart_tmov_32_3079328b98d6.svg) |
| `bstart_tmov_32_34d0ab432974` | `BSTART.TMOV DataType` | 32 | — | [SVG](../wavedrom/enc_bstart_tmov_32_34d0ab432974.svg) |
| `bstart_tmov_32_472804576301` | `BSTART.TMOV DataType` | 32 | — | [SVG](../wavedrom/enc_bstart_tmov_32_472804576301.svg) |
| `bstart_tmov_32_d96181e99f01` | `BSTART.TMOV DataType` | 32 | — | [SVG](../wavedrom/enc_bstart_tmov_32_d96181e99f01.svg) |
| `bstart_tmov_32_efe5c49fcb78` | `BSTART.TMOV DataType` | 32 | — | [SVG](../wavedrom/enc_bstart_tmov_32_efe5c49fcb78.svg) |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
