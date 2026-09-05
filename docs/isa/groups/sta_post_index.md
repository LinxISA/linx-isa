# STA/POST_INDEX

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** STA/POST_INDEX &nbsp;|&nbsp;
**Forms:** 14 &nbsp;|&nbsp;
**Unique mnemonics:** 14

</div>

Instructions in the **STA/POST_INDEX** group of the LinxISA v0.58.6 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.SB.PO](../instructions/hl_sb_po.md) | `hl.sb.po SrcD, [SrcL, SrcR<{.sw,.uw}>], ->{t, u, Rd}` | 48 | — | HL.SB.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [HL.SBI.PO](../instructions/hl_sbi_po.md) | `hl.sbi.po SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SBI.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [HL.SD.PO](../instructions/hl_sd_po.md) | `hl.sd.po SrcD, [SrcL, SrcR<{.sw,.uw}><<3], ->{t, u, Rd}` | 48 | — | HL.SD.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SD.UPO](../instructions/hl_sd_upo.md) | `hl.sd.upo SrcD, [SrcL, SrcR<{.sw,.uw}>], ->{t, u, Rd}` | 48 | — | HL.SD.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SDI.PO](../instructions/hl_sdi_po.md) | `hl.sdi.po SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SDI.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SDI.UPO](../instructions/hl_sdi_upo.md) | `hl.sdi.upo SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SDI.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SH.PO](../instructions/hl_sh_po.md) | `hl.sh.po SrcD, [SrcL, SrcR<{.sw,.uw}><<1], ->{t, u, Rd}` | 48 | — | HL.SH.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SH.UPO](../instructions/hl_sh_upo.md) | `hl.sh.upo SrcD, [SrcL, SrcR<{.sw,.uw}>], ->{t, u, Rd}` | 48 | — | HL.SH.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SHI.PO](../instructions/hl_shi_po.md) | `hl.shi.po SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SHI.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SHI.UPO](../instructions/hl_shi_upo.md) | `hl.shi.upo SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SHI.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SW.PO](../instructions/hl_sw_po.md) | `hl.sw.po SrcD, [SrcL, SrcR<{.sw,.uw}><<2], ->{t, u, Rd}` | 48 | — | HL.SW.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SW.UPO](../instructions/hl_sw_upo.md) | `hl.sw.upo SrcD, [SrcL, SrcR<{.sw,.uw}>], ->{t, u, Rd}` | 48 | — | HL.SW.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SWI.PO](../instructions/hl_swi_po.md) | `hl.swi.po SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SWI.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SWI.UPO](../instructions/hl_swi_upo.md) | `hl.swi.upo SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | HL.SWI.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
