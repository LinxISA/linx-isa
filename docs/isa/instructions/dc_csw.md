# DC.CSW

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/sys.md">SYS</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `dc.csw SrcL`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_dc_csw.svg" alt="DC.CSW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

DC.CSW completes the data-cache clean-by-set/way scope token maintenance operation synchronously.

## Pseudocode (informative)

```c
// Execute DC.CSW as defined by the SYS semantics.
```

## Encoding Notes

- `DC.CSW completes the data-cache clean-by-set/way scope token maintenance operation synchronously.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `dc.csw SrcL` | 32 | — |

<div class="insn-nav">

← [SYS](../groups/sys.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
