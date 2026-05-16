# Load Pre-Index

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** Load Pre-Index &nbsp;|&nbsp;
**Forms:** 19 &nbsp;|&nbsp;
**Unique mnemonics:** 19

</div>

Load with pre-index writeback.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.LB.PR](../instructions/hl_lb_pr.md) | `hl.lb.pr [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBI.PR](../instructions/hl_lbi_pr.md) | `hl.lbi.pr [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBU.PR](../instructions/hl_lbu_pr.md) | `hl.lbu.pr [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBUI.PR](../instructions/hl_lbui_pr.md) | `hl.lbui.pr [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LD.PR](../instructions/hl_ld_pr.md) | `hl.ld.pr [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDI.PR](../instructions/hl_ldi_pr.md) | `hl.ldi.pr [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDI.UPR](../instructions/hl_ldi_upr.md) | `hl.ldi.upr [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LH.PR](../instructions/hl_lh_pr.md) | `hl.lh.pr [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHI.PR](../instructions/hl_lhi_pr.md) | `hl.lhi.pr [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHI.UPR](../instructions/hl_lhi_upr.md) | `hl.lhi.upr [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHU.PR](../instructions/hl_lhu_pr.md) | `hl.lhu.pr [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUI.PR](../instructions/hl_lhui_pr.md) | `hl.lhui.pr [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUI.UPR](../instructions/hl_lhui_upr.md) | `hl.lhui.upr [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LW.PR](../instructions/hl_lw_pr.md) | `hl.lw.pr [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWI.PR](../instructions/hl_lwi_pr.md) | `hl.lwi.pr [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWI.UPR](../instructions/hl_lwi_upr.md) | `hl.lwi.upr [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWU.PR](../instructions/hl_lwu_pr.md) | `hl.lwu.pr [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUI.PR](../instructions/hl_lwui_pr.md) | `hl.lwui.pr [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUI.UPR](../instructions/hl_lwui_upr.md) | `hl.lwui.upr [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
