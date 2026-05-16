# HL.SSRGET

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/ssr_access.md">SSR Access</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.ssrget SSR_ID, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_ssrget.svg" alt="HL.SSRGET encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

[48-bit HL.] Instruction from the SSR Access group.

## Pseudocode (informative)

```c
// Execute HL.SSRGET as defined by the SSR Access semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.ssrget SSR_ID, ->{t, u, Rd}` | 48 | — |

<div class="insn-nav">

← [SSR Access](../groups/ssr_access.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
