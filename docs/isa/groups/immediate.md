# Immediate

<div class="insn-header">

<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Group:** Immediate &nbsp;|&nbsp;
**Forms:** 2 &nbsp;|&nbsp;
**Unique mnemonics:** 2

</div>

Immediate materialization instructions (LUI, ADDTPC, HL.LUI).

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.LUI](../instructions/hl_lui.md) | `hl.lui imm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Immediate group. |
| [LUI](../instructions/lui.md) | `lui simm, ->{t, u, Rd}` | 32 | — | Load upper immediate. Materializes a 20-bit constant in the upper bits of the destination. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 12: ALU — Arithmetic Logic Unit](../index.md)
- [Encoding formats](../encoding.md)
