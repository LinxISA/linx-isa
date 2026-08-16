# DC.CIVA

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/sys.md">SYS</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `dc.civa SrcL`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_dc_civa.svg" alt="DC.CIVA encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

DC.CIVA completes the data-cache clean-and-invalidate scope token maintenance operation synchronously.

## Pseudocode (informative)

```c
// Execute DC.CIVA as defined by the SYS semantics.
```

## Encoding Notes

- `DC.CIVA completes the data-cache clean-and-invalidate scope token maintenance operation synchronously.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `dc.civa SrcL` | 32 | — |

<div class="insn-nav">

← [SYS](../groups/sys.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
