# Arithmetic Operation 32bit

<div class="insn-header">

<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Group:** Arithmetic Operation 32bit &nbsp;|&nbsp;
**Forms:** 21 &nbsp;|&nbsp;
**Unique mnemonics:** 21

</div>

32-bit (word) integer arithmetic instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [ADDIW](../instructions/addiw.md) | `addiw SrcL, uimm, ->{t, u, Rd}` | 32 | — | 32-bit word add-immediate. |
| [ADDW](../instructions/addw.md) | `addw SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>, ->{t, u, Rd}` | 32 | — | 32-bit word integer addition. |
| [ANDIW](../instructions/andiw.md) | `andiw SrcL, simm, ->{t, u, Rd}` | 32 | — | 32-bit word AND-immediate. |
| [ANDW](../instructions/andw.md) | `andw SrcL, SrcR<{.sw,.uw,.not}><<<shamt>, ->{t, u, Rd}` | 32 | — | 32-bit word bitwise AND. |
| [HL.ADDIW](../instructions/hl_addiw.md) | `hl.addiw SrcL, uimm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Arithmetic Operation 32bit group. |
| [HL.ANDIW](../instructions/hl_andiw.md) | `hl.andiw SrcL, simm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Arithmetic Operation 32bit group. |
| [HL.ORIW](../instructions/hl_oriw.md) | `hl.oriw SrcL, simm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Arithmetic Operation 32bit group. |
| [HL.SUBIW](../instructions/hl_subiw.md) | `hl.subiw SrcL, uimm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Arithmetic Operation 32bit group. |
| [HL.XORIW](../instructions/hl_xoriw.md) | `hl.xoriw SrcL, simm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Arithmetic Operation 32bit group. |
| [ORIW](../instructions/oriw.md) | `oriw SrcL, simm, ->{t, u, Rd}` | 32 | — | 32-bit word OR-immediate. |
| [ORW](../instructions/orw.md) | `orw SrcL, SrcR<{.sw,.uw,.not}><<<shamt>, ->{t, u, Rd}` | 32 | — | 32-bit word bitwise OR. |
| [SLLIW](../instructions/slliw.md) | `slliw SrcL, shamt, ->{t, u, Rd}` | 32 | — | 32-bit word logical left shift (immediate). |
| [SLLW](../instructions/sllw.md) | `sllw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word logical left shift. |
| [SRAIW](../instructions/sraiw.md) | `sraiw SrcL, shamt, ->{t, u, Rd}` | 32 | — | 32-bit word arithmetic right shift (immediate). |
| [SRAW](../instructions/sraw.md) | `sraw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word arithmetic right shift. |
| [SRLIW](../instructions/srliw.md) | `srliw SrcL, shamt, ->{t, u, Rd}` | 32 | — | 32-bit word logical right shift (immediate). |
| [SRLW](../instructions/srlw.md) | `srlw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word logical right shift. |
| [SUBIW](../instructions/subiw.md) | `subiw SrcL, uimm, ->{t, u, Rd}` | 32 | — | Instruction from the Arithmetic Operation 32bit group. |
| [SUBW](../instructions/subw.md) | `subw SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>, ->{t, u, Rd}` | 32 | — | 32-bit word integer subtraction. |
| [XORIW](../instructions/xoriw.md) | `xoriw SrcL, simm, ->{t, u, Rd}` | 32 | — | 32-bit word XOR-immediate. |
| [XORW](../instructions/xorw.md) | `xorw SrcL, SrcR<{.sw,.uw,.not}><<<shamt>, ->{t, u, Rd}` | 32 | — | 32-bit word bitwise XOR. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 12: ALU — Arithmetic Logic Unit](../index.md)
- [Encoding formats](../encoding.md)
