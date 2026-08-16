# C.BSTART

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/bundle_split.md">Bundle Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `C.BSTART DIRECT, label`
- `C.BSTART COND,  label`

## Encoding

<div class="enc-diagram">

<figure id="encoding-c_bstart_16_78ebf9b37d2d">
<img src="../wavedrom/enc_c_bstart_16_78ebf9b37d2d.svg" alt="C.BSTART encoding form c_bstart_16_78ebf9b37d2d" width="100%" />
<figcaption><code>c_bstart_16_78ebf9b37d2d</code> — <code>C.BSTART DIRECT, label</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-c_bstart_16_b82b9a0c292c">
<img src="../wavedrom/enc_c_bstart_16_b82b9a0c292c.svg" alt="C.BSTART encoding form c_bstart_16_b82b9a0c292c" width="100%" />
<figcaption><code>c_bstart_16_b82b9a0c292c</code> — <code>C.BSTART COND, label</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

</div>

## Description

[16-bit C.] Terminates the current block and begins the next.

## Pseudocode (informative)

```c
EndBlock(); BeginNextBlock(/* kind */);
```

## Encoding Notes

- `Starts a compressed standard block with a PC-relative direct or conditional candidate target.`

## Full Catalog Forms

| Form ID | Assembly | Length | Decode | Encoding |
|---------|----------|--------|--------|----------|
| `c_bstart_16_78ebf9b37d2d` | `C.BSTART DIRECT, label` | 16 | — | [SVG](../wavedrom/enc_c_bstart_16_78ebf9b37d2d.svg) |
| `c_bstart_16_b82b9a0c292c` | `C.BSTART COND,  label` | 16 | — | [SVG](../wavedrom/enc_c_bstart_16_b82b9a0c292c.svg) |

<div class="insn-nav">

← [Bundle Split](../groups/bundle_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
