# L.BSTART.STD

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bstart.md">BSTART</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>64</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `L.BSTART.STD COND, <label>`
- `L.BSTART.STD DIRECT, <label>`
- `L.BSTART.STD CALL, <label>`
- `L.BSTART.STD FALL<, fixup_label>`

## Encoding

<div class="enc-diagram">

<figure id="encoding-l_bstart_std_64_40bf385dbbff">
<img src="../wavedrom/enc_l_bstart_std_64_40bf385dbbff.svg" alt="L.BSTART.STD encoding form l_bstart_std_64_40bf385dbbff" width="100%" />
<figcaption><code>l_bstart_std_64_40bf385dbbff</code> — <code>L.BSTART.STD COND, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-l_bstart_std_64_49b7cf990e62">
<img src="../wavedrom/enc_l_bstart_std_64_49b7cf990e62.svg" alt="L.BSTART.STD encoding form l_bstart_std_64_49b7cf990e62" width="100%" />
<figcaption><code>l_bstart_std_64_49b7cf990e62</code> — <code>L.BSTART.STD DIRECT, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-l_bstart_std_64_9a6081ab8f08">
<img src="../wavedrom/enc_l_bstart_std_64_9a6081ab8f08.svg" alt="L.BSTART.STD encoding form l_bstart_std_64_9a6081ab8f08" width="100%" />
<figcaption><code>l_bstart_std_64_9a6081ab8f08</code> — <code>L.BSTART.STD CALL, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-l_bstart_std_64_ed61315d3418">
<img src="../wavedrom/enc_l_bstart_std_64_ed61315d3418.svg" alt="L.BSTART.STD encoding form l_bstart_std_64_ed61315d3418" width="100%" />
<figcaption><code>l_bstart_std_64_ed61315d3418</code> — <code>L.BSTART.STD FALL<, fixup_label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

</div>

## Description

Instruction from the BSTART group.

## Pseudocode (informative)

```c
// Execute L.BSTART.STD as defined by the BSTART semantics.
```

## Encoding Notes

- `Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind.`
- `Bare L.BSTART.STD CALL preserves ra. A returning call must be preceded by SETRET or C.SETRET with an explicit return label.`

## Full Catalog Forms

| Form ID | Assembly | Length | Decode | Encoding |
|---------|----------|--------|--------|----------|
| `l_bstart_std_64_40bf385dbbff` | `L.BSTART.STD COND, <label>` | 64 | — | [SVG](../wavedrom/enc_l_bstart_std_64_40bf385dbbff.svg) |
| `l_bstart_std_64_49b7cf990e62` | `L.BSTART.STD DIRECT, <label>` | 64 | — | [SVG](../wavedrom/enc_l_bstart_std_64_49b7cf990e62.svg) |
| `l_bstart_std_64_9a6081ab8f08` | `L.BSTART.STD CALL, <label>` | 64 | — | [SVG](../wavedrom/enc_l_bstart_std_64_9a6081ab8f08.svg) |
| `l_bstart_std_64_ed61315d3418` | `L.BSTART.STD FALL<, fixup_label>` | 64 | — | [SVG](../wavedrom/enc_l_bstart_std_64_ed61315d3418.svg) |

<div class="insn-nav">

← [BSTART](../groups/bstart.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
