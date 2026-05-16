# Store Pre-Index

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** Store Pre-Index &nbsp;|&nbsp;
**Forms:** 14 &nbsp;|&nbsp;
**Unique mnemonics:** 14

</div>

Store with pre-index writeback.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.SB.PR](../instructions/hl_sb_pr.md) | `hl.sb.pr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SBI.PR](../instructions/hl_sbi_pr.md) | `hl.sbi.pr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SD.PR](../instructions/hl_sd_pr.md) | `hl.sd.pr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<3], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SD.UPR](../instructions/hl_sd_upr.md) | `hl.sd.upr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SDI.PR](../instructions/hl_sdi_pr.md) | `hl.sdi.pr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SDI.UPR](../instructions/hl_sdi_upr.md) | `hl.sdi.upr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SH.PR](../instructions/hl_sh_pr.md) | `hl.sh.pr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<1], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SH.UPR](../instructions/hl_sh_upr.md) | `hl.sh.upr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SHI.PR](../instructions/hl_shi_pr.md) | `hl.shi.pr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SHI.UPR](../instructions/hl_shi_upr.md) | `hl.shi.upr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SW.PR](../instructions/hl_sw_pr.md) | `hl.sw.pr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<2], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SW.UPR](../instructions/hl_sw_upr.md) | `hl.sw.upr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SWI.PR](../instructions/hl_swi_pr.md) | `hl.swi.pr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SWI.UPR](../instructions/hl_swi_upr.md) | `hl.swi.upr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
