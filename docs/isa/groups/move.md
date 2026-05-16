# Move

<div class="insn-header">

<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Group:** Move &nbsp;|&nbsp;
**Forms:** 3 &nbsp;|&nbsp;
**Unique mnemonics:** 3

</div>

Register/memory move instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [C.MOVI](../instructions/c_movi.md) | `c.movi simm, ->{t, u, Rd}` | 16 | — | [16-bit C.] Instruction from the Move group. |
| [C.MOVR](../instructions/c_movr.md) | `c.movr SrcL, ->{t, u, Rd}` | 16 | — | [16-bit C.] Instruction from the Move group. |
| [C.SETRET](../instructions/c_setret.md) | `c.setret uimm, - >Ra` | 16 | — | [16-bit C.] Instruction from the Move group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 12: ALU — Arithmetic Logic Unit](../index.md)
- [Encoding formats](../encoding.md)
