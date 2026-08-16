# C.EBREAK

<div class="insn-header">

<span class="badge-16">16-bit C.</span> **Group:** <a href="../groups/sys.md">SYS</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Length:** <code>16</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `c.break imm`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_c_ebreak.svg" alt="C.EBREAK encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

C.EBREAK raises software-breakpoint trap 50 with its 5-bit immediate as cause.

## Pseudocode (informative)

```c
Trap(EBREAK);
```

## Encoding Notes

- `C.EBREAK raises software-breakpoint trap 50 with its 5-bit immediate as cause.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `c.break imm` | 16 | — |

<div class="insn-nav">

← [SYS](../groups/sys.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
