# HL.SSRSET

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/sys.md">SYS</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.ssrset SrcL, SSR_ID`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_ssrset.svg" alt="HL.SSRSET encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.SSRSET writes the complete encoded system-register address.

## Pseudocode (informative)

```c
// Execute HL.SSRSET as defined by the SYS semantics.
```

## Encoding Notes

- `HL.SSRSET writes the complete encoded system-register address.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.ssrset SrcL, SSR_ID` | 48 | — |

<div class="insn-nav">

← [SYS](../groups/sys.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
