# C.BSTART

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/block_split.md">Block Split</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `C.BSTART COND,  label`
- `C.BSTART DIRECT, label`

## Encoding

<div class="enc-diagram">

<figure id="encoding-c_bstart_16_c4e238a9227a">
<img src="../wavedrom/enc_c_bstart_16_c4e238a9227a.svg" alt="C.BSTART encoding form c_bstart_16_c4e238a9227a" width="100%" />
<figcaption><code>c_bstart_16_c4e238a9227a</code> — <code>C.BSTART COND, label</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-c_bstart_16_f833d2a4753c">
<img src="../wavedrom/enc_c_bstart_16_f833d2a4753c.svg" alt="C.BSTART encoding form c_bstart_16_f833d2a4753c" width="100%" />
<figcaption><code>c_bstart_16_f833d2a4753c</code> — <code>C.BSTART DIRECT, label</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

</div>

## Description

[16-bit C.] Terminates the current block and begins the next.

## Pseudocode (informative)

```c
EndBlock(); BeginNextBlock(/* kind */);
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Form ID | Assembly | Length | Decode | Encoding |
|---------|----------|--------|--------|----------|
| `c_bstart_16_c4e238a9227a` | `C.BSTART COND,  label` | 16 | — | [SVG](../wavedrom/enc_c_bstart_16_c4e238a9227a.svg) |
| `c_bstart_16_f833d2a4753c` | `C.BSTART DIRECT, label` | 16 | — | [SVG](../wavedrom/enc_c_bstart_16_f833d2a4753c.svg) |

<div class="insn-nav">

← [Block Split](../groups/block_split.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
