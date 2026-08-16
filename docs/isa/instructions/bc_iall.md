# BC.IALL

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/sys.md">SYS</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `bc.iall`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_bc_iall.svg" alt="BC.IALL encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Branch-predictor cache invalidate all entries.

## Pseudocode (informative)

```c
// Execute BC.IALL as defined by the SYS semantics.
```

## Encoding Notes

- `BC.IALL completes the bundle-cache all-entry scope maintenance operation synchronously.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `bc.iall` | 32 | — |

<div class="insn-nav">

← [SYS](../groups/sys.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
