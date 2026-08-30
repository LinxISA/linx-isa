# STA/PRE_INDEX

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** STA/PRE_INDEX &nbsp;|&nbsp;
**Forms:** 14 &nbsp;|&nbsp;
**Unique mnemonics:** 14

</div>

Instructions in the **STA/PRE_INDEX** group of the LinxISA v0.58.5 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.SB.PR](../instructions/hl_sb_pr.md) | `hl.sb.pr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>], ->{t, u, Rd}` | 48 | — | HL.SB.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [HL.SBI.PR](../instructions/hl_sbi_pr.md) | `hl.sbi.pr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SBI.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [HL.SD.PR](../instructions/hl_sd_pr.md) | `hl.sd.pr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<3], ->{t, u, Rd}` | 48 | — | HL.SD.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SD.UPR](../instructions/hl_sd_upr.md) | `hl.sd.upr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>], ->{t, u, Rd}` | 48 | — | HL.SD.UPR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SDI.PR](../instructions/hl_sdi_pr.md) | `hl.sdi.pr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SDI.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SDI.UPR](../instructions/hl_sdi_upr.md) | `hl.sdi.upr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SDI.UPR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SH.PR](../instructions/hl_sh_pr.md) | `hl.sh.pr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<1], ->{t, u, Rd}` | 48 | — | HL.SH.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SH.UPR](../instructions/hl_sh_upr.md) | `hl.sh.upr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>], ->{t, u, Rd}` | 48 | — | HL.SH.UPR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SHI.PR](../instructions/hl_shi_pr.md) | `hl.shi.pr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SHI.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SHI.UPR](../instructions/hl_shi_upr.md) | `hl.shi.upr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SHI.UPR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SW.PR](../instructions/hl_sw_pr.md) | `hl.sw.pr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<2], ->{t, u, Rd}` | 48 | — | HL.SW.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SW.UPR](../instructions/hl_sw_upr.md) | `hl.sw.upr SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>], ->{t, u, Rd}` | 48 | — | HL.SW.UPR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SWI.PR](../instructions/hl_swi_pr.md) | `hl.swi.pr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SWI.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SWI.UPR](../instructions/hl_swi_upr.md) | `hl.swi.upr SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SWI.UPR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
