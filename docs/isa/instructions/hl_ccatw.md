# HL.CCATW

<div class="insn-header">

<span class="badge-48">48-bit HL.</span> **Group:** <a href="../groups/concat.md">Concat</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-18">Ch 18</span>
&nbsp; <strong>RSV — Reserved and Indexed Operations</strong> &nbsp;|&nbsp;
**Length:** <code>48</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `hl.ccatw SrcL, SrcR, shamt, ->Dst0, Dst1`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_hl_ccatw.svg" alt="HL.CCATW encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

HL.CCATW - Concatenate two 32-bit values into a sign-extended result pair.

## Pseudocode (informative)

```c
// Execute HL.CCATW as defined by the Concat semantics.
```

## Encoding Notes

- `HL.CCATW - Concatenate two 32-bit values into a sign-extended result pair.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `hl.ccatw SrcL, SrcR, shamt, ->Dst0, Dst1` | 48 | — |

<div class="insn-nav">

← [Concat](../groups/concat.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
