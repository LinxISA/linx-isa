# Compound Operation

<div class="insn-header">

<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Group:** Compound Operation &nbsp;|&nbsp;
**Forms:** 1 &nbsp;|&nbsp;
**Unique mnemonics:** 1

</div>

Compound operations (e.g., conditional select).

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [CSEL](../instructions/csel.md) | `csel SrcP, SrcL, SrcR<.neg>, ->{t, u, Rd}` | 32 | — | Conditional select. `Dest = (SrcP != 0) ? SrcL : SrcR`. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 12: ALU — Arithmetic Logic Unit](../index.md)
- [Encoding formats](../encoding.md)
