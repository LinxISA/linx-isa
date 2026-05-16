# HL.PRFI.UA

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/prefetch.md">Prefetch</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.prfi.ua{.l1,.l2,.l3} [SrcL, simm], ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_prfi_ua.svg" alt="HL.PRFI.UA encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[48-bit HL.] Instruction from the Prefetch group.

## Pseudocode (informative)

```c
// Execute HL.PRFI.UA as defined by the Prefetch semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.prfi.ua{.l1,.l2,.l3} [SrcL, simm], ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [Prefetch](../groups/prefetch.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
