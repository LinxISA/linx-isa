# Arithmetic Operation 64bit

<div class="insn-header">

<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Group:** Arithmetic Operation 64bit &nbsp;|&nbsp;
**Forms:** 21 &nbsp;|&nbsp;
**Unique mnemonics:** 21

</div>

Full 64-bit integer arithmetic instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [ADD](../instructions/add.md) | `add SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>, ->{t, u, Rd}` | 32 | — | Integer addition. Writes the sum of two registers to the destination. |
| [ADDI](../instructions/addi.md) | `addi SrcL, uimm, ->{t, u, Rd}` | 32 | — | Integer add-immediate. Adds a sign-extended 12-bit immediate to a register. |
| [AND](../instructions/and.md) | `and SrcL, SrcR<{.sw,.uw,.not}><<<shamt>, ->{t, u, Rd}` | 32 | — | Bitwise AND of two registers. |
| [ANDI](../instructions/andi.md) | `andi SrcL, simm, ->{t, u, Rd}` | 32 | — | Bitwise AND with an immediate. |
| [HL.ADDI](../instructions/hl_addi.md) | `hl.addi SrcL, uimm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Arithmetic Operation 64bit group. |
| [HL.ANDI](../instructions/hl_andi.md) | `hl.andi SrcL, simm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Arithmetic Operation 64bit group. |
| [HL.ORI](../instructions/hl_ori.md) | `hl.ori SrcL, simm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Arithmetic Operation 64bit group. |
| [HL.SUBI](../instructions/hl_subi.md) | `hl.subi SrcL, uimm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Arithmetic Operation 64bit group. |
| [HL.XORI](../instructions/hl_xori.md) | `hl.xori SrcL, simm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Arithmetic Operation 64bit group. |
| [OR](../instructions/or.md) | `or SrcL, SrcR<{.sw,.uw,.not}><<<shamt>, ->{t, u, Rd}` | 32 | — | Bitwise OR of two registers. |
| [ORI](../instructions/ori.md) | `ori SrcL, simm, ->{t, u, Rd}` | 32 | — | Bitwise OR with an immediate. |
| [SLL](../instructions/sll.md) | `sll SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Logical left shift by the value in SrcR. |
| [SLLI](../instructions/slli.md) | `slli SrcL, shamt, ->{t, u, Rd}` | 32 | — | Logical left shift by an immediate amount. |
| [SRA](../instructions/sra.md) | `sra SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Arithmetic right shift by the value in SrcR. |
| [SRAI](../instructions/srai.md) | `srai SrcL, shamt, ->{t, u, Rd}` | 32 | — | Arithmetic right shift by an immediate amount. |
| [SRL](../instructions/srl.md) | `srl SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Logical right shift by the value in SrcR. |
| [SRLI](../instructions/srli.md) | `srli SrcL, shamt, ->{t, u, Rd}` | 32 | — | Logical right shift by an immediate amount. |
| [SUB](../instructions/sub.md) | `sub SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>, ->{t, u, Rd}` | 32 | — | Integer subtraction. |
| [SUBI](../instructions/subi.md) | `subi SrcL, uimm, ->{t, u, Rd}` | 32 | — | Instruction from the Arithmetic Operation 64bit group. |
| [XOR](../instructions/xor.md) | `xor SrcL, SrcR<{.sw,.uw,.not}><<<shamt>, ->{t, u, Rd}` | 32 | — | Bitwise XOR of two registers. |
| [XORI](../instructions/xori.md) | `xori SrcL, simm, ->{t, u, Rd}` | 32 | — | Bitwise XOR with an immediate. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 12: ALU — Arithmetic Logic Unit](../index.md)
- [Encoding formats](../encoding.md)
