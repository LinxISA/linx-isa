# SYNC.CORE

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/sys.md">SYS</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `sync.core`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_sync_core.svg" alt="SYNC.CORE encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Waits for all four PEs at the same Core-local phase boundary and completes their earlier GM obligations.

## Pseudocode (informative)

```c
// Execute SYNC.CORE as defined by the SYS semantics.
```

## Encoding Notes

- `Waits for all four PEs at the same Core-local phase boundary and completes their earlier GM obligations.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `sync.core` | 32 | — |

<div class="insn-nav">

← [SYS](../groups/sys.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
