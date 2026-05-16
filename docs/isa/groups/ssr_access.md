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
| [HL.SSRGET](../instructions/hl_ssrget.md) | `hl.ssrget SSR_ID, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the SSR Access group. |
| [HL.SSRSET](../instructions/hl_ssrset.md) | `hl.ssrset SrcL, SSR_ID` | 48 | — | [48-bit HL.] Instruction from the SSR Access group. |
| [LSRGET](../instructions/lsrget.md) | `lsrget LSR_ID, ->{t, u, Rd}` | 32 | — | Instruction from the SSR Access group. |
| [SETC.TGT](../instructions/setc_tgt.md) | `setc.tgt SrcL` | 32 | — | Sets the block-commit condition. |
| [SSRGET](../instructions/ssrget.md) | `ssrget SSR_ID, ->{t, u, Rd}` | 32 | — | Instruction from the SSR Access group. |
| [SSRSET](../instructions/ssrset.md) | `ssrset SrcL, SSR_ID` | 32 | — | Instruction from the SSR Access group. |
| [SSRSWAP](../instructions/ssrswap.md) | `ssrswap SrcL, SSR_ID, ->{t, u, Rd}` | 32 | — | Instruction from the SSR Access group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 19: SYS — System Operations](../index.md)
- [Encoding formats](../encoding.md)
