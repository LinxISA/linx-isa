# PC-Relative

<div class="insn-header">

<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Group:** PC-Relative &nbsp;|&nbsp;
**Forms:** 4 &nbsp;|&nbsp;
**Unique mnemonics:** 4

</div>

PC-relative address computation instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [ADDTPC](../instructions/addtpc.md) | `addtpc simm, ->{t, u, Rd}` | 32 | — | PC-relative addition. Adds an immediate to the current PC/TPC and writes the result. |
| [HL.ADDTPC](../instructions/hl_addtpc.md) | `hl.addtpc imm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the PC-Relative group. |
| [HL.SETRET](../instructions/hl_setret.md) | `hl.setret imm, ->Ra` | 48 | — | [48-bit HL.] Instruction from the PC-Relative group. |
| [SETRET](../instructions/setret.md) | `setret uimm, ->Ra` | 32 | — | Materializes a return address (ra) using a PC-relative offset. Used in call headers. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 16: BRU — Branch and Compare](../index.md)
- [Encoding formats](../encoding.md)
