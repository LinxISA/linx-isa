# SSR Access

<div class="insn-header">

<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Group:** SSR Access &nbsp;|&nbsp;
**Forms:** 7 &nbsp;|&nbsp;
**Unique mnemonics:** 7

</div>

System register (SSR/LSR) access instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.SSRGET](../instructions/hl_ssrget.md) | `hl.ssrget SSR_ID, ->{t, u, Rd}` | 48 | — | HL.SSRGET - Read the addressed system register. |
| [HL.SSRSET](../instructions/hl_ssrset.md) | `hl.ssrset SrcL, SSR_ID` | 48 | — | HL.SSRSET - Write the addressed system register. |
| [LSRGET](../instructions/lsrget.md) | `lsrget LSR_ID, ->{t, u, Rd}` | 32 | — | LSRGET - Read the addressed system register. |
| [SETC.TGT](../instructions/setc_tgt.md) | `setc.tgt SrcL` | 32 | — | Sets the block-commit condition. |
| [SSRGET](../instructions/ssrget.md) | `ssrget SSR_ID, ->{t, u, Rd}` | 32 | — | SSRGET - Read the addressed system register. |
| [SSRSET](../instructions/ssrset.md) | `ssrset SrcL, SSR_ID` | 32 | — | SSRSET - Write the addressed system register. |
| [SSRSWAP](../instructions/ssrswap.md) | `ssrswap SrcL, SSR_ID, ->{t, u, Rd}` | 32 | — | SSRSWAP - Atomically exchange the addressed system register and scalar value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 19: SYS — System Operations](../index.md)
- [Encoding formats](../encoding.md)
