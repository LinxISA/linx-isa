# Concat

<div class="insn-header">

<span class="ch-tag ch-tag-18">Ch 18</span>
&nbsp; <strong>RSV — Reserved and Indexed Operations</strong> &nbsp;|&nbsp;
**Group:** Concat &nbsp;|&nbsp;
**Forms:** 2 &nbsp;|&nbsp;
**Unique mnemonics:** 2

</div>

Concatenation / combine operations.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.CCAT](../instructions/hl_ccat.md) | `hl.ccat SrcL, SrcR, shamt, ->Dst0, Dst1` | 48 | — | HL.CCAT - Concatenate two scalar values into a result pair. |
| [HL.CCATW](../instructions/hl_ccatw.md) | `hl.ccatw SrcL, SrcR, shamt, ->Dst0, Dst1` | 48 | — | HL.CCATW - Concatenate two 32-bit values into a sign-extended result pair. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 18: RSV — Reserved and Indexed Operations](../index.md)
- [Encoding formats](../encoding.md)
