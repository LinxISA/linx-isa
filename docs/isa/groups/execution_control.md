# Execution Control

<div class="insn-header">

<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Group:** Execution Control &nbsp;|&nbsp;
**Forms:** 10 &nbsp;|&nbsp;
**Unique mnemonics:** 10

</div>

Architectural control, EBREAK, ASSERT, ACR operations.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [ACRC](../instructions/acrc.md) | `acrc rst_type` | 32 | — | Architectural control (ring call). Calls an implementation-defined ACR. |
| [ACRE](../instructions/acre.md) | `acre rra_type` | 32 | — | Architectural control (ring entry). Enters an implementation-defined ACR. |
| [ASSERT](../instructions/assert.md) | `assert SrcL` | 32 | — | Architectural assertion. Traps if the condition register is zero. |
| [BSE](../instructions/bse.md) | `bse SrcL` | 32 | — | Execution control instruction. |
| [BWE](../instructions/bwe.md) | `bwe SrcL` | 32 | — | Execution control instruction. |
| [BWI](../instructions/bwi.md) | `bwi SrcL` | 32 | — | Execution control instruction. |
| [BWT](../instructions/bwt.md) | `bwt SrcL` | 32 | — | Execution control instruction. |
| [EBREAK](../instructions/ebreak.md) | `ebreak imm` | 32 | — | Environment break instruction. Traps to the debugging or OS handler. |
| [FENCE.D](../instructions/fence_d.md) | `fence.d pred_imm, succ_imm` | 32 | — | Data memory ordering fence. |
| [FENCE.I](../instructions/fence_i.md) | `fence.i` | 32 | — | Instruction-cache fence. Synchronizes instruction fetch with prior stores. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 19: SYS — System Operations](../index.md)
- [Encoding formats](../encoding.md)
