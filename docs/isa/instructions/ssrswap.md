# SSRSWAP

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/ssr_access.md">SSR Access</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `ssrswap SrcL, SSR_ID, ->{t, u, Rd}`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_ssrswap.svg" alt="SSRSWAP encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Instruction from the SSR Access group.

## Pseudocode (informative)

```c
// Execute SSRSWAP as defined by the SSR Access semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `ssrswap SrcL, SSR_ID, ->{t, u, Rd}` | 32 | — |

<div class="insn-nav">

← [SSR Access](../groups/ssr_access.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
