# Compare Instruction

<div class="insn-header">

<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Group:** Compare Instruction &nbsp;|&nbsp;
**Forms:** 40 &nbsp;|&nbsp;
**Unique mnemonics:** 40

</div>

Integer comparison instructions that write a boolean result.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [CMP.AND](../instructions/cmp_and.md) | `cmp.and SrcL, SrcR<.sw, .uw, .not>, ->{t, u, Rd}` | 32 | — | Instruction from the Compare Instruction group. |
| [CMP.ANDI](../instructions/cmp_andi.md) | `cmp.andi SrcL, simm, ->{t, u, Rd}` | 32 | — | Instruction from the Compare Instruction group. |
| [CMP.EQ](../instructions/cmp_eq.md) | `cmp.eq SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — | Compare equal. Sets destination to 1 if operands are equal. |
| [CMP.EQI](../instructions/cmp_eqi.md) | `cmp.eqi SrcL, simm, ->{t, u, Rd}` | 32 | — | Instruction from the Compare Instruction group. |
| [CMP.GE](../instructions/cmp_ge.md) | `cmp.ge SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — | Compare greater-or-equal (signed). |
| [CMP.GEI](../instructions/cmp_gei.md) | `cmp.gei SrcL, simm, ->{t, u, Rd}` | 32 | — | Instruction from the Compare Instruction group. |
| [CMP.GEU](../instructions/cmp_geu.md) | `cmp.geu SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — | Compare greater-or-equal (unsigned). |
| [CMP.GEUI](../instructions/cmp_geui.md) | `cmp.geui SrcL, uimm, ->{t, u, Rd}` | 32 | — | Instruction from the Compare Instruction group. |
| [CMP.LT](../instructions/cmp_lt.md) | `cmp.lt SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — | Compare less-than (signed). |
| [CMP.LTI](../instructions/cmp_lti.md) | `cmp.lti SrcL, simm, ->{t, u, Rd}` | 32 | — | Instruction from the Compare Instruction group. |
| [CMP.LTU](../instructions/cmp_ltu.md) | `cmp.ltu SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — | Compare less-than (unsigned). |
| [CMP.LTUI](../instructions/cmp_ltui.md) | `cmp.ltui SrcL, uimm, ->{t, u, Rd}` | 32 | — | Instruction from the Compare Instruction group. |
| [CMP.NE](../instructions/cmp_ne.md) | `cmp.ne SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — | Compare not-equal. |
| [CMP.NEI](../instructions/cmp_nei.md) | `cmp.nei SrcL, simm, ->{t, u, Rd}` | 32 | — | Instruction from the Compare Instruction group. |
| [CMP.OR](../instructions/cmp_or.md) | `cmp.or SrcL, SrcR<.sw, .uw, .not>, ->{t, u, Rd}` | 32 | — | Instruction from the Compare Instruction group. |
| [CMP.ORI](../instructions/cmp_ori.md) | `cmp.ori SrcL, simm, ->{t, u, Rd}` | 32 | — | Instruction from the Compare Instruction group. |
| [HL.CMP.ANDI](../instructions/hl_cmp_andi.md) | `hl.cmp.andi SrcL, simm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.EQI](../instructions/hl_cmp_eqi.md) | `hl.cmp.eqi SrcL, simm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.GEI](../instructions/hl_cmp_gei.md) | `hl.cmp.gei SrcL, simm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.GEUI](../instructions/hl_cmp_geui.md) | `hl.cmp.geui SrcL, uimm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.LTI](../instructions/hl_cmp_lti.md) | `hl.cmp.lti SrcL, simm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.LTUI](../instructions/hl_cmp_ltui.md) | `hl.cmp.ltui SrcL, uimm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.NEI](../instructions/hl_cmp_nei.md) | `hl.cmp.nei SrcL, simm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.ORI](../instructions/hl_cmp_ori.md) | `hl.cmp.ori SrcL, simm, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Instruction from the Compare Instruction group. |
| [V.CMP.AND](../instructions/v_cmp_and.md) | `v.cmp.and SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.ANDI](../instructions/v_cmp_andi.md) | `v.cmp.andi SrcL, simm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.EQ](../instructions/v_cmp_eq.md) | `v.cmp.eq SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.EQI](../instructions/v_cmp_eqi.md) | `v.cmp.eqi SrcL, simm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.GE](../instructions/v_cmp_ge.md) | `v.cmp.ge SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.GEI](../instructions/v_cmp_gei.md) | `v.cmp.gei SrcL, simm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.GEU](../instructions/v_cmp_geu.md) | `v.cmp.geu SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.GEUI](../instructions/v_cmp_geui.md) | `v.cmp.geui SrcL, uimm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.LT](../instructions/v_cmp_lt.md) | `v.cmp.lt SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.LTI](../instructions/v_cmp_lti.md) | `v.cmp.lti SrcL, simm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.LTU](../instructions/v_cmp_ltu.md) | `v.cmp.ltu SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.LTUI](../instructions/v_cmp_ltui.md) | `v.cmp.ltui SrcL, uimm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.NE](../instructions/v_cmp_ne.md) | `v.cmp.ne SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.NEI](../instructions/v_cmp_nei.md) | `v.cmp.nei SrcL, simm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.OR](../instructions/v_cmp_or.md) | `v.cmp.or SrcL, SrcR, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.ORI](../instructions/v_cmp_ori.md) | `v.cmp.ori SrcL, simm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Compare Instruction group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 16: BRU — Branch and Compare](../index.md)
- [Encoding formats](../encoding.md)
