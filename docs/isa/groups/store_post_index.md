# Store Post-Index

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** Store Post-Index &nbsp;|&nbsp;
**Forms:** 14 &nbsp;|&nbsp;
**Unique mnemonics:** 14

</div>

Store with post-index writeback.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.SB.PO](../instructions/hl_sb_po.md) | `hl.sb.po SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SBI.PO](../instructions/hl_sbi_po.md) | `hl.sbi.po SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SD.PO](../instructions/hl_sd_po.md) | `hl.sd.po SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<3], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SD.UPO](../instructions/hl_sd_upo.md) | `hl.sd.upo SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SDI.PO](../instructions/hl_sdi_po.md) | `hl.sdi.po SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SDI.UPO](../instructions/hl_sdi_upo.md) | `hl.sdi.upo SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SH.PO](../instructions/hl_sh_po.md) | `hl.sh.po SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<1], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SH.UPO](../instructions/hl_sh_upo.md) | `hl.sh.upo SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SHI.PO](../instructions/hl_shi_po.md) | `hl.shi.po SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SHI.UPO](../instructions/hl_shi_upo.md) | `hl.shi.upo SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SW.PO](../instructions/hl_sw_po.md) | `hl.sw.po SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<2], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SW.UPO](../instructions/hl_sw_upo.md) | `hl.sw.upo SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SWI.PO](../instructions/hl_swi_po.md) | `hl.swi.po SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SWI.UPO](../instructions/hl_swi_upo.md) | `hl.swi.upo SrcD, [SrcR, simm], ->{t, u, Rd}` | 48 | — | [48-bit HL.] Stores a register value to memory. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
