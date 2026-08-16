# SW.PCR

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/sta.md">STA</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `sw.pcr SrcL, [symbol]`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_sw_pcr.svg" alt="SW.PCR encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

SW.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value.

## Pseudocode (informative)

```c
// Execute SW.PCR as defined by the STA semantics.
```

## Encoding Notes

- `SW.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `sw.pcr SrcL, [symbol]` | 32 | — |

<div class="insn-nav">

← [STA](../groups/sta.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
