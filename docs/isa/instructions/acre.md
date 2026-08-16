# ACRE

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/sys.md">SYS</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `acre rra_type`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_acre.svg" alt="ACRE encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Architectural control (ring entry). Enters an implementation-defined ACR.

## Pseudocode (informative)

```c
// Execute ACRE as defined by the SYS semantics.
```

## Encoding Notes

- `ACRE atomically commits the active SYS block and recovers one validated architecture context.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `acre rra_type` | 32 | — |

<div class="insn-nav">

← [SYS](../groups/sys.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
