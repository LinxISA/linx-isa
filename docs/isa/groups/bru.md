# BRU

<div class="insn-header">

<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Group:** BRU &nbsp;|&nbsp;
**Forms:** 66 &nbsp;|&nbsp;
**Unique mnemonics:** 66

</div>

Instructions in the **BRU** group of the LinxISA v0.58.1 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [ADDTPC](../instructions/addtpc.md) | `addtpc simm, ->{t, u, Rd}` | 32 | — | PC-relative addition. Adds an immediate to the current PC/TPC and writes the result. |
| [B.EQ](../instructions/b_eq.md) | `b.eq SrcL, SrcR, label` | 32 | — | Conditional branch taken when SrcL equals SrcR. |
| [B.GE](../instructions/b_ge.md) | `b.ge SrcL, SrcR, label` | 32 | — | Conditional branch taken when SrcL is greater than or equal to SrcR (signed). |
| [B.GEU](../instructions/b_geu.md) | `b.geu SrcL, SrcR, label` | 32 | — | Conditional branch taken when SrcL is greater than or equal to SrcR (unsigned). |
| [B.LT](../instructions/b_lt.md) | `b.lt SrcL, SrcR, label` | 32 | — | Conditional branch taken when SrcL is less than SrcR (signed). |
| [B.LTU](../instructions/b_ltu.md) | `b.ltu SrcL, SrcR, label` | 32 | — | Conditional branch taken when SrcL is less than SrcR (unsigned). |
| [B.NE](../instructions/b_ne.md) | `b.ne SrcL, SrcR, label` | 32 | — | Conditional branch taken when SrcL not equal to SrcR. |
| [B.NZ](../instructions/b_nz.md) | `b.nz label` | 32 | — | B.NZ - Conditionally branch to the PC-relative target after comparing scalar operands. |
| [B.Z](../instructions/b_z.md) | `b.z label` | 32 | — | B.Z - Conditionally branch to the PC-relative target after comparing scalar operands. |
| [C.CMP.EQI](../instructions/c_cmp_eqi.md) | `c.cmp.eqi t#1, simm, ->t` | 16 | — | C.CMP.EQI - Compare scalar operands and write the encoded boolean result. |
| [C.CMP.NEI](../instructions/c_cmp_nei.md) | `c.cmp.nei t#1, simm, ->t` | 16 | — | C.CMP.NEI - Compare scalar operands and write the encoded boolean result. |
| [C.SETC.EQ](../instructions/c_setc_eq.md) | `c.setc.eq srcL, srcR` | 16 | — | [16-bit C.] Sets the block-commit condition. |
| [C.SETC.NE](../instructions/c_setc_ne.md) | `c.setc.ne srcL, srcR` | 16 | — | [16-bit C.] Sets the block-commit condition. |
| [CMP.AND](../instructions/cmp_and.md) | `cmp.and SrcL, SrcR<.sw, .uw, .not>, ->{t, u, Rd}` | 32 | — | CMP.AND - Combine scalar comparison results with the encoded logical operation. |
| [CMP.ANDI](../instructions/cmp_andi.md) | `cmp.andi SrcL, simm, ->{t, u, Rd}` | 32 | — | CMP.ANDI - Combine scalar comparison results with the encoded logical operation. |
| [CMP.EQ](../instructions/cmp_eq.md) | `cmp.eq SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — | Compare equal. Sets destination to 1 if operands are equal. |
| [CMP.EQI](../instructions/cmp_eqi.md) | `cmp.eqi SrcL, simm, ->{t, u, Rd}` | 32 | — | CMP.EQI - Compare scalar operands and write the encoded boolean result. |
| [CMP.GE](../instructions/cmp_ge.md) | `cmp.ge SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — | Compare greater-or-equal (signed). |
| [CMP.GEI](../instructions/cmp_gei.md) | `cmp.gei SrcL, simm, ->{t, u, Rd}` | 32 | — | CMP.GEI - Compare scalar operands and write the encoded boolean result. |
| [CMP.GEU](../instructions/cmp_geu.md) | `cmp.geu SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — | Compare greater-or-equal (unsigned). |
| [CMP.GEUI](../instructions/cmp_geui.md) | `cmp.geui SrcL, uimm, ->{t, u, Rd}` | 32 | — | CMP.GEUI - Compare scalar operands and write the encoded boolean result. |
| [CMP.LT](../instructions/cmp_lt.md) | `cmp.lt SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — | Compare less-than (signed). |
| [CMP.LTI](../instructions/cmp_lti.md) | `cmp.lti SrcL, simm, ->{t, u, Rd}` | 32 | — | CMP.LTI - Compare scalar operands and write the encoded boolean result. |
| [CMP.LTU](../instructions/cmp_ltu.md) | `cmp.ltu SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — | Compare less-than (unsigned). |
| [CMP.LTUI](../instructions/cmp_ltui.md) | `cmp.ltui SrcL, uimm, ->{t, u, Rd}` | 32 | — | CMP.LTUI - Compare scalar operands and write the encoded boolean result. |
| [CMP.NE](../instructions/cmp_ne.md) | `cmp.ne SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}` | 32 | — | Compare not-equal. |
| [CMP.NEI](../instructions/cmp_nei.md) | `cmp.nei SrcL, simm, ->{t, u, Rd}` | 32 | — | CMP.NEI - Compare scalar operands and write the encoded boolean result. |
| [CMP.OR](../instructions/cmp_or.md) | `cmp.or SrcL, SrcR<.sw, .uw, .not>, ->{t, u, Rd}` | 32 | — | CMP.OR - Combine scalar comparison results with the encoded logical operation. |
| [CMP.ORI](../instructions/cmp_ori.md) | `cmp.ori SrcL, simm, ->{t, u, Rd}` | 32 | — | CMP.ORI - Combine scalar comparison results with the encoded logical operation. |
| [HL.ADDTPC](../instructions/hl_addtpc.md) | `hl.addtpc imm, ->{t, u, Rd}` | 48 | — | HL.ADDTPC - Add the encoded displacement to the program counter. |
| [HL.CMP.ANDI](../instructions/hl_cmp_andi.md) | `hl.cmp.andi SrcL, simm, ->{t, u, Rd}` | 48 | — | HL.CMP.ANDI - Combine scalar comparison results with the encoded logical operation. |
| [HL.CMP.EQI](../instructions/hl_cmp_eqi.md) | `hl.cmp.eqi SrcL, simm, ->{t, u, Rd}` | 48 | — | HL.CMP.EQI - Compare scalar operands and write the encoded boolean result. |
| [HL.CMP.GEI](../instructions/hl_cmp_gei.md) | `hl.cmp.gei SrcL, simm, ->{t, u, Rd}` | 48 | — | HL.CMP.GEI - Compare scalar operands and write the encoded boolean result. |
| [HL.CMP.GEUI](../instructions/hl_cmp_geui.md) | `hl.cmp.geui SrcL, uimm, ->{t, u, Rd}` | 48 | — | HL.CMP.GEUI - Compare scalar operands and write the encoded boolean result. |
| [HL.CMP.LTI](../instructions/hl_cmp_lti.md) | `hl.cmp.lti SrcL, simm, ->{t, u, Rd}` | 48 | — | HL.CMP.LTI - Compare scalar operands and write the encoded boolean result. |
| [HL.CMP.LTUI](../instructions/hl_cmp_ltui.md) | `hl.cmp.ltui SrcL, uimm, ->{t, u, Rd}` | 48 | — | HL.CMP.LTUI - Compare scalar operands and write the encoded boolean result. |
| [HL.CMP.NEI](../instructions/hl_cmp_nei.md) | `hl.cmp.nei SrcL, simm, ->{t, u, Rd}` | 48 | — | HL.CMP.NEI - Compare scalar operands and write the encoded boolean result. |
| [HL.CMP.ORI](../instructions/hl_cmp_ori.md) | `hl.cmp.ori SrcL, simm, ->{t, u, Rd}` | 48 | — | HL.CMP.ORI - Combine scalar comparison results with the encoded logical operation. |
| [HL.SETC.ANDI](../instructions/hl_setc_andi.md) | `hl.setc.andi SrcL, simm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.EQI](../instructions/hl_setc_eqi.md) | `hl.setc.eqi SrcL, simm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.GEI](../instructions/hl_setc_gei.md) | `hl.setc.gei SrcL, simm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.GEUI](../instructions/hl_setc_geui.md) | `hl.setc.geui SrcL, uimm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.LTI](../instructions/hl_setc_lti.md) | `hl.setc.lti SrcL, simm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.LTUI](../instructions/hl_setc_ltui.md) | `hl.setc.ltui SrcL, uimm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.NEI](../instructions/hl_setc_nei.md) | `hl.setc.nei SrcL, simm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.ORI](../instructions/hl_setc_ori.md) | `hl.setc.ori SrcL, simm` | 48 | — | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETRET](../instructions/hl_setret.md) | `hl.setret imm, ->Ra` | 48 | — | HL.SETRET - Write the architectural return address. |
| [J](../instructions/j.md) | `j label` | 32 | — | Unconditional PC-relative jump to a target label. |
| [JR](../instructions/jr.md) | `jr SrcL, label` | 32 | — | Jump register: PC-relative or register-based jump to the address in a register. |
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
| [SETRET](../instructions/setret.md) | `setret uimm, ->Ra` | 32 | — | Materializes a return address (ra) using a PC-relative offset. Used in call headers. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 16: BRU — Branch and Compare](../index.md)
- [Encoding formats](../encoding.md)
