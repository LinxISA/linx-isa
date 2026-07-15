# L.BSTART.STD

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bstart.md">BSTART</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `L.BSTART.STD DIRECT, <label>`
- `L.BSTART.STD CALL, <label>`
- `L.BSTART.STD COND, <label>`
- `L.BSTART.STD FALL<, fixup_label>`

## Encoding

<div class="enc-diagram">

<figure id="encoding-l_bstart_std_64_37e84068ce61">
<img src="../wavedrom/enc_l_bstart_std_64_37e84068ce61.svg" alt="L.BSTART.STD encoding form l_bstart_std_64_37e84068ce61" width="100%" />
<figcaption><code>l_bstart_std_64_37e84068ce61</code> — <code>L.BSTART.STD DIRECT, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-l_bstart_std_64_463a1567da91">
<img src="../wavedrom/enc_l_bstart_std_64_463a1567da91.svg" alt="L.BSTART.STD encoding form l_bstart_std_64_463a1567da91" width="100%" />
<figcaption><code>l_bstart_std_64_463a1567da91</code> — <code>L.BSTART.STD CALL, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-l_bstart_std_64_72d502fcd30d">
<img src="../wavedrom/enc_l_bstart_std_64_72d502fcd30d.svg" alt="L.BSTART.STD encoding form l_bstart_std_64_72d502fcd30d" width="100%" />
<figcaption><code>l_bstart_std_64_72d502fcd30d</code> — <code>L.BSTART.STD COND, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-l_bstart_std_64_899592f9c5bc">
<img src="../wavedrom/enc_l_bstart_std_64_899592f9c5bc.svg" alt="L.BSTART.STD encoding form l_bstart_std_64_899592f9c5bc" width="100%" />
<figcaption><code>l_bstart_std_64_899592f9c5bc</code> — <code>L.BSTART.STD FALL<, fixup_label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

</div>

## Description

Instruction from the BSTART group.

## Pseudocode (informative)

```c
// Execute L.BSTART.STD as defined by the BSTART semantics.
```

## Encoding Notes

- `Bare L.BSTART.STD CALL preserves ra. A returning call must be preceded by SETRET or C.SETRET with an explicit return label.`

## Full Catalog Forms

| Form ID | Assembly | Length | Decode | Encoding |
|---------|----------|--------|--------|----------|
| `l_bstart_std_64_37e84068ce61` | `L.BSTART.STD DIRECT, <label>` | 64 | — | [SVG](../wavedrom/enc_l_bstart_std_64_37e84068ce61.svg) |
| `l_bstart_std_64_463a1567da91` | `L.BSTART.STD CALL, <label>` | 64 | — | [SVG](../wavedrom/enc_l_bstart_std_64_463a1567da91.svg) |
| `l_bstart_std_64_72d502fcd30d` | `L.BSTART.STD COND, <label>` | 64 | — | [SVG](../wavedrom/enc_l_bstart_std_64_72d502fcd30d.svg) |
| `l_bstart_std_64_899592f9c5bc` | `L.BSTART.STD FALL<, fixup_label>` | 64 | — | [SVG](../wavedrom/enc_l_bstart_std_64_899592f9c5bc.svg) |

<div class="insn-nav">

← [BSTART](../groups/bstart.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
