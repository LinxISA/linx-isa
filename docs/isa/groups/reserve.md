# RESERVE

<div class="insn-header">

<span class="ch-tag ch-tag-18">Ch 18</span>
&nbsp; <strong>RSV — Reserved and Indexed Operations</strong> &nbsp;|&nbsp;
**Group:** RESERVE &nbsp;|&nbsp;
**Forms:** 3 &nbsp;|&nbsp;
**Unique mnemonics:** 3

</div>

Reservation and conditional-update operations.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.BFI](../instructions/hl_bfi.md) | `hl.bfi SrcL, SrcR, M, N, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Bit-field insert. |
| [HL.MIADD](../instructions/hl_miadd.md) | `hl.miadd SrcL, SrcR, uimm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the RESERVE group. |
| [HL.MISUB](../instructions/hl_misub.md) | `hl.misub SrcL, SrcR, uimm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the RESERVE group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 18: RSV — Reserved and Indexed Operations](../index.md)
- [Encoding formats](../encoding.md)
