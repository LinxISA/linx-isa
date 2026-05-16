# Multi-Cycle ALU

<div class="insn-header">

<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Group:** Multi-Cycle ALU &nbsp;|&nbsp;
**Forms:** 28 &nbsp;|&nbsp;
**Unique mnemonics:** 28

</div>

Multi-cycle ALU operations: division, remainder, and extended multiply.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [DIV](../instructions/div.md) | `div SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Signed integer division. |
| [DIVU](../instructions/divu.md) | `divu SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Unsigned integer division. |
| [DIVUW](../instructions/divuw.md) | `divuw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word unsigned integer division. |
| [DIVW](../instructions/divw.md) | `divw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word signed integer division. |
| [HL.DIV](../instructions/hl_div.md) | `hl.div SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Signed integer division. |
| [HL.DIVU](../instructions/hl_divu.md) | `hl.divu SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Unsigned integer division. |
| [HL.DIVUW](../instructions/hl_divuw.md) | `hl.divuw SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.DIVW](../instructions/hl_divw.md) | `hl.divw SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.MADD](../instructions/hl_madd.md) | `hl.madd SrcL, SrcR, SrcD, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.MADDW](../instructions/hl_maddw.md) | `hl.maddw SrcL, SrcR, SrcD, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.MUL](../instructions/hl_mul.md) | `hl.mul SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Integer multiply. |
| [HL.MULU](../instructions/hl_mulu.md) | `hl.mulu SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.REM](../instructions/hl_rem.md) | `hl.rem SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Signed integer remainder. |
| [HL.REMU](../instructions/hl_remu.md) | `hl.remu SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Unsigned integer remainder. |
| [HL.REMUW](../instructions/hl_remuw.md) | `hl.remuw SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.REMW](../instructions/hl_remw.md) | `hl.remw SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [MADD](../instructions/madd.md) | `madd SrcL, SrcR, SrcD, ->{t, u, Rd}` | 32 | — | Multiply-add: `Dest = SrcD + SrcL * SrcR`. |
| [MADDW](../instructions/maddw.md) | `maddw SrcL, SrcR, SrcD, ->{t, u, Rd}` | 32 | — | 32-bit word multiply-add. |
| [MUL](../instructions/mul.md) | `mul SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Integer multiply (lower product written to destination). |
| [MULU](../instructions/mulu.md) | `mulu SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Integer multiply (unsigned). |
| [MULUW](../instructions/muluw.md) | `muluw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word integer multiply (unsigned). |
| [MULW](../instructions/mulw.md) | `mulw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word integer multiply. |
| [REM](../instructions/rem.md) | `rem SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Signed integer remainder. |
| [REMU](../instructions/remu.md) | `remu SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Unsigned integer remainder. |
| [REMUW](../instructions/remuw.md) | `remuw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word unsigned remainder. |
| [REMW](../instructions/remw.md) | `remw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word signed remainder. |
| [V.MADD](../instructions/v_madd.md) | `v.madd SrcL, SrcR, SrcD, ->Dst` | 64 | — | [64-bit V.] Instruction from the Multi-Cycle ALU group. |
| [V.MUL](../instructions/v_mul.md) | `v.mul SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Integer multiply. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 12: ALU — Arithmetic Logic Unit](../index.md)
- [Encoding formats](../encoding.md)
