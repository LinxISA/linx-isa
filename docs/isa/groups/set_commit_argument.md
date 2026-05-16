# Set Commit Argument

<div class="insn-header">

<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Group:** Set Commit Argument &nbsp;|&nbsp;
**Forms:** 26 &nbsp;|&nbsp;
**Unique mnemonics:** 26

</div>

SETC instructions that encode the block-commit condition.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [C.SETC.EQ](../instructions/c_setc_eq.md) | `c.setc.eq srcL, srcR` | 16 | — | [16-bit C.] Sets the block-commit condition. |
| [C.SETC.NE](../instructions/c_setc_ne.md) | `c.setc.ne srcL, srcR` | 16 | — | [16-bit C.] Sets the block-commit condition. |
| [HL.SETC.ANDI](../instructions/hl_setc_andi.md) | `hl.setc.andi SrcL, simm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.EQI](../instructions/hl_setc_eqi.md) | `hl.setc.eqi SrcL, simm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.GEI](../instructions/hl_setc_gei.md) | `hl.setc.gei SrcL, simm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.GEUI](../instructions/hl_setc_geui.md) | `hl.setc.geui SrcL, uimm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.LTI](../instructions/hl_setc_lti.md) | `hl.setc.lti SrcL, simm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.LTUI](../instructions/hl_setc_ltui.md) | `hl.setc.ltui SrcL, uimm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.NEI](../instructions/hl_setc_nei.md) | `hl.setc.nei SrcL, simm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.ORI](../instructions/hl_setc_ori.md) | `hl.setc.ori SrcL, simm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [SETC.AND](../instructions/setc_and.md) | `setc.and SrcL, SrcR<.sw, .uw, .not>` | 32 | — | Sets the block-commit condition. |
| [SETC.ANDI](../instructions/setc_andi.md) | `setc.andi SrcL, simm` | 32 | — | Sets the block-commit condition. |
| [SETC.EQ](../instructions/setc_eq.md) | `setc.eq SrcL, SrcR<{.sw, .uw}>` | 32 | — | Sets the block-commit condition. |
| [SETC.EQI](../instructions/setc_eqi.md) | `setc.eqi SrcL, simm` | 32 | — | Sets the block-commit condition. |
| [SETC.GE](../instructions/setc_ge.md) | `setc.ge SrcL, SrcR<{.sw, .uw}>` | 32 | — | Sets the block-commit condition. |
| [SETC.GEI](../instructions/setc_gei.md) | `setc.gei SrcL, simm` | 32 | — | Sets the block-commit condition. |
| [SETC.GEU](../instructions/setc_geu.md) | `setc.geu SrcL, SrcR<{.sw, .uw}>` | 32 | — | Sets the block-commit condition. |
| [SETC.GEUI](../instructions/setc_geui.md) | `setc.geui SrcL, uimm` | 32 | — | Sets the block-commit condition. |
| [SETC.LT](../instructions/setc_lt.md) | `setc.lt SrcL, SrcR<{.sw, .uw}>` | 32 | — | Sets the block-commit condition. |
| [SETC.LTI](../instructions/setc_lti.md) | `setc.lti SrcL, simm` | 32 | — | Sets the block-commit condition. |
| [SETC.LTU](../instructions/setc_ltu.md) | `setc.ltu SrcL, SrcR<{.sw, .uw}>` | 32 | — | Sets the block-commit condition. |
| [SETC.LTUI](../instructions/setc_ltui.md) | `setc.ltui SrcL, uimm` | 32 | — | Sets the block-commit condition. |
| [SETC.NE](../instructions/setc_ne.md) | `setc.ne SrcL, SrcR<{.sw, .uw}>` | 32 | — | Sets the block-commit condition. |
| [SETC.NEI](../instructions/setc_nei.md) | `setc.nei SrcL, simm` | 32 | — | Sets the block-commit condition. |
| [SETC.OR](../instructions/setc_or.md) | `setc.or SrcL, SrcR<.sw, .uw, .not>` | 32 | — | Sets the block-commit condition. |
| [SETC.ORI](../instructions/setc_ori.md) | `setc.ori SrcL, simm` | 32 | — | Sets the block-commit condition. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 16: BRU — Branch and Compare](../index.md)
- [Encoding formats](../encoding.md)
