# LDA/POST_INDEX

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** LDA/POST_INDEX &nbsp;|&nbsp;
**Forms:** 19 &nbsp;|&nbsp;
**Unique mnemonics:** 19

</div>

Instructions in the **LDA/POST_INDEX** group of the LinxISA v0.58.1 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.LB.PO](../instructions/hl_lb_po.md) | `hl.lb.po [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LB.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBI.PO](../instructions/hl_lbi_po.md) | `hl.lbi.po [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LBI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBU.PO](../instructions/hl_lbu_po.md) | `hl.lbu.po [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LBU.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBUI.PO](../instructions/hl_lbui_po.md) | `hl.lbui.po [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LBUI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LD.PO](../instructions/hl_ld_po.md) | `hl.ld.po [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LD.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LDI.PO](../instructions/hl_ldi_po.md) | `hl.ldi.po [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LDI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LDI.UPO](../instructions/hl_ldi_upo.md) | `hl.ldi.upo [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LDI.UPO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LH.PO](../instructions/hl_lh_po.md) | `hl.lh.po [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LH.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHI.PO](../instructions/hl_lhi_po.md) | `hl.lhi.po [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LHI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHI.UPO](../instructions/hl_lhi_upo.md) | `hl.lhi.upo [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LHI.UPO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHU.PO](../instructions/hl_lhu_po.md) | `hl.lhu.po [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LHU.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHUI.PO](../instructions/hl_lhui_po.md) | `hl.lhui.po [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LHUI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHUI.UPO](../instructions/hl_lhui_upo.md) | `hl.lhui.upo [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LHUI.UPO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LW.PO](../instructions/hl_lw_po.md) | `hl.lw.po [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LW.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWI.PO](../instructions/hl_lwi_po.md) | `hl.lwi.po [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LWI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWI.UPO](../instructions/hl_lwi_upo.md) | `hl.lwi.upo [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LWI.UPO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWU.PO](../instructions/hl_lwu_po.md) | `hl.lwu.po [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LWU.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWUI.PO](../instructions/hl_lwui_po.md) | `hl.lwui.po [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LWUI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWUI.UPO](../instructions/hl_lwui_upo.md) | `hl.lwui.upo [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LWUI.UPO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
