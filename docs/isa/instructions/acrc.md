# ACRC

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/execution_control.md">Execution Control</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `acrc rst_type`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_acrc.svg" alt="ACRC encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Architectural control (ring call). Calls an implementation-defined ACR.

## Pseudocode (informative)

```c
// Execute ACRC as defined by the Execution Control semantics.
```

## Encoding Notes

_No additional encoding notes._

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `acrc rst_type` | 32 | — |

<div class="insn-nav">

← [Execution Control](../groups/execution_control.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
