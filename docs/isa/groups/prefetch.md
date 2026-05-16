# Prefetch

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** Prefetch &nbsp;|&nbsp;
**Forms:** 4 &nbsp;|&nbsp;
**Unique mnemonics:** 4

</div>

Memory prefetch hint instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.PRF](../instructions/hl_prf.md) | `hl.prf{.l1,.l2,.l3} [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>]` | 48 | — | [48-bit HL.] Instruction from the Prefetch group. |
| [HL.PRF.A](../instructions/hl_prf_a.md) | `hl.prf.a{.l1,.l2,.l3} [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Prefetch group. |
| [HL.PRFI.U](../instructions/hl_prfi_u.md) | `hl.prfi.u{.l1,.l2,.l3} [SrcL, simm]` | 48 | — | [48-bit HL.] Instruction from the Prefetch group. |
| [HL.PRFI.UA](../instructions/hl_prfi_ua.md) | `hl.prfi.ua{.l1,.l2,.l3} [SrcL, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Prefetch group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
