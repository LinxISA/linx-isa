# C.SSRGET

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/sys.md">SYS</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.ssrget SSR-ID, ->t`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_ssrget.svg" alt="C.SSRGET encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

C.SSRGET reads the complete encoded system-register address.

## Pseudocode (informative)

```c
// Execute C.SSRGET as defined by the SYS semantics.
```

## Encoding Notes

- `C.SSRGET reads the complete encoded system-register address.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.ssrget SSR-ID, ->t` | 16 | — |

<div class="insn-nav">

← [SYS](../groups/sys.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
