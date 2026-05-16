# Atomic

<div class="insn-header">

<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Group:** Atomic &nbsp;|&nbsp;
**Forms:** 4 &nbsp;|&nbsp;
**Unique mnemonics:** 4

</div>

Atomic memory operations including load-reserved, store-conditional, and fetch-op variants.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.CASB](../instructions/hl_casb.md) | `hl.casb<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Atomic memory read-modify-write operation. |
| [HL.CASD](../instructions/hl_casd.md) | `hl.casd<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Atomic memory read-modify-write operation. |
| [HL.CASH](../instructions/hl_cash.md) | `hl.cash<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Atomic memory read-modify-write operation. |
| [HL.CASW](../instructions/hl_casw.md) | `hl.casw<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Atomic memory read-modify-write operation. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 14: AMO — Atomic Memory Operations](../index.md)
- [Encoding formats](../encoding.md)
