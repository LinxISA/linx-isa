# Arithmetic Operation

<div class="insn-header">

<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Group:** Arithmetic Operation &nbsp;|&nbsp;
**Forms:** 20 &nbsp;|&nbsp;
**Unique mnemonics:** 20

</div>

Extended integer arithmetic, including 64-bit forms and vector variants.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [C.ADD](../instructions/c_add.md) | `c.add srcL, srcR, ->t` | 16 | — | [16-bit C.] Integer addition. |
| [C.AND](../instructions/c_and.md) | `c.and srcL, srcR, ->t` | 16 | — | [16-bit C.] Bitwise AND. |
| [C.OR](../instructions/c_or.md) | `c.or srcL, srcR, ->t` | 16 | — | [16-bit C.] Bitwise OR. |
| [C.SUB](../instructions/c_sub.md) | `c.sub srcL, srcR, ->t` | 16 | — | [16-bit C.] Integer subtraction. |
| [V.ADD](../instructions/v_add.md) | `v.add SrcL, SrcR<.neg><<<shamt>, ->Dst` | 64 | — | [64-bit V.] Integer addition. |
| [V.ADDI](../instructions/v_addi.md) | `v.addi SrcL, uimm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.AND](../instructions/v_and.md) | `v.and SrcL, SrcR<.not><<<shamt>, ->Dst` | 64 | — | [64-bit V.] Bitwise AND. |
| [V.ANDI](../instructions/v_andi.md) | `v.andi SrcL, simm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.OR](../instructions/v_or.md) | `v.or SrcL, SrcR<.not><<<shamt>, ->Dst` | 64 | — | [64-bit V.] Bitwise OR. |
| [V.ORI](../instructions/v_ori.md) | `v.ori SrcL, simm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.SLL](../instructions/v_sll.md) | `v.sll SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Logical left shift. |
| [V.SLLI](../instructions/v_slli.md) | `v.slli SrcL, shamt, ->Dst` | 64 | — | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.SRA](../instructions/v_sra.md) | `v.sra SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Arithmetic right shift. |
| [V.SRAI](../instructions/v_srai.md) | `v.srai SrcL, shamt, ->Dst` | 64 | — | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.SRL](../instructions/v_srl.md) | `v.srl SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Logical right shift. |
| [V.SRLI](../instructions/v_srli.md) | `v.srli SrcL, shamt, ->Dst` | 64 | — | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.SUB](../instructions/v_sub.md) | `v.sub SrcL, SrcR<.neg><<<shamt>, ->Dst` | 64 | — | [64-bit V.] Integer subtraction. |
| [V.SUBI](../instructions/v_subi.md) | `v.subi SrcL, uimm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.XOR](../instructions/v_xor.md) | `v.xor SrcL, SrcR<.not><<<shamt>, ->Dst` | 64 | — | [64-bit V.] Bitwise XOR. |
| [V.XORI](../instructions/v_xori.md) | `v.xori SrcL, simm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Arithmetic Operation group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 12: ALU — Arithmetic Logic Unit](../index.md)
- [Encoding formats](../encoding.md)
