# HL.BSTART.STD

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/bstart.md">BSTART</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `HL.BSTART.STD CALL, <label>`
- `HL.BSTART.STD FALL<, fixup_label>`
- `HL.BSTART.STD COND, <label>`
- `HL.BSTART.STD DIRECT, <label>`

## Encoding

<div class="enc-diagram">

<figure id="encoding-hl_bstart_std_48_51f78942222e">
<img src="../wavedrom/enc_hl_bstart_std_48_51f78942222e.svg" alt="HL.BSTART.STD encoding form hl_bstart_std_48_51f78942222e" width="100%" />
<figcaption><code>hl_bstart_std_48_51f78942222e</code> — <code>HL.BSTART.STD CALL, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-hl_bstart_std_48_9ba705710872">
<img src="../wavedrom/enc_hl_bstart_std_48_9ba705710872.svg" alt="HL.BSTART.STD encoding form hl_bstart_std_48_9ba705710872" width="100%" />
<figcaption><code>hl_bstart_std_48_9ba705710872</code> — <code>HL.BSTART.STD FALL<, fixup_label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-hl_bstart_std_48_b13f22c7c4a3">
<img src="../wavedrom/enc_hl_bstart_std_48_b13f22c7c4a3.svg" alt="HL.BSTART.STD encoding form hl_bstart_std_48_b13f22c7c4a3" width="100%" />
<figcaption><code>hl_bstart_std_48_b13f22c7c4a3</code> — <code>HL.BSTART.STD COND, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-hl_bstart_std_48_d814d26508a4">
<img src="../wavedrom/enc_hl_bstart_std_48_d814d26508a4.svg" alt="HL.BSTART.STD encoding form hl_bstart_std_48_d814d26508a4" width="100%" />
<figcaption><code>hl_bstart_std_48_d814d26508a4</code> — <code>HL.BSTART.STD DIRECT, <label></code>. MSB is on the left, LSB is on the right.</figcaption>
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
| `hl_bstart_std_48_51f78942222e` | `HL.BSTART.STD CALL, <label>` | 48 | — | [SVG](../wavedrom/enc_hl_bstart_std_48_51f78942222e.svg) |
| `hl_bstart_std_48_9ba705710872` | `HL.BSTART.STD FALL<, fixup_label>` | 48 | — | [SVG](../wavedrom/enc_hl_bstart_std_48_9ba705710872.svg) |
| `hl_bstart_std_48_b13f22c7c4a3` | `HL.BSTART.STD COND, <label>` | 48 | — | [SVG](../wavedrom/enc_hl_bstart_std_48_b13f22c7c4a3.svg) |
| `hl_bstart_std_48_d814d26508a4` | `HL.BSTART.STD DIRECT, <label>` | 48 | — | [SVG](../wavedrom/enc_hl_bstart_std_48_d814d26508a4.svg) |

<div class="insn-nav">

← [BSTART](../groups/bstart.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
