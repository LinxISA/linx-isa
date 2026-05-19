# Comparison instructions

This part of the instructions is used for data comparison and setting, supporting signed and unsigned comparisons as well as register-register and register-immediate comparison services.

For instructions whose two inputs are registers and registers, you can selectively intercept the low bits of the right source register with or without sign extension. Logical comparison instructions (setc.and and setc.or) can invert the right source register and then compare.

**Register-Register Comparison**

| Microinstructions | Assembly format | Description |
|---------------|---------------------------|----------------------------------------------|
| CMP.EQ | cmp.eq SrcL, SrcR<{.sw, .uw}>, ->{t,u,Rd} | Equal comparison |
| CMP.NE | cmp.ne SrcL, SrcR<{.sw, .uw}>, ->{t,u,Rd} | Not equal comparison |
| CMP.AND | cmp.and SrcL, SrcR<{.sw, .uw, .not}>, ->{t,u,Rd} | Phase and comparison |
| CMP.OR | cmp.or SrcL, SrcR<{.sw, .uw, .not}>, ->{t,u,Rd} | Phase OR comparison |
| CMP.LT | cmp.lt SrcL, SrcR<{.sw, .uw}>, ->{t,u,Rd} | Signed less than comparison |
| CMP.GE | cmp.ge SrcL, SrcR<{.sw, .uw}>, ->{t,u,Rd} | Signed greater than or equal comparison |
| CMP.LTU | cmp.ltu SrcL, SrcR<{.sw, .uw}>, ->{t,u,Rd} | Unsigned less than comparison |
| CMP.GEU | cmp.geu SrcL, SrcR<{.sw, .uw}>, ->{t,u,Rd} | Unsigned greater than or equal comparison |

The encoding format is as follows:

![CompareInstruction](../../../figs/bitfield/svg/Introduction_32bit/CompareInstruction.svg)

**Register-immediate comparison**| Microinstructions | Assembly format | Description |
|---------------|---------------------------|----------------------------------------------|
| CMP.EQI | cmp.eqi SrcL, simm, ->{t,u,Rd} | Signed immediate equals comparison |
| CMP.NEI | cmp.nei SrcL, simm, ->{t,u,Rd} | Signed immediate is not equal to comparison |
| CMP.ANDI | cmp.andi SrcL, simm, ->{t,u,Rd} | Signed immediate AND comparison |
| CMP.ORI | cmp.ori SrcL, simm, ->{t,u,Rd} | Signed immediate OR comparison |
| CMP.LTI | cmp.lti SrcL, simm, ->{t,u,Rd} | Signed immediate less than comparison |
| CMP.GEI | cmp.gei SrcL, simm, ->{t,u,Rd} | Signed immediate greater than or equal comparison |
| CMP.LTUI | cmp.ltui SrcL, uimm, ->{t,u,Rd} | Unsigned immediate less than comparison |
| CMP.GEUI | cmp.geui SrcL, uimm, ->{t,u,Rd} | Unsigned immediate greater than or equal comparison |

![ComparewithimmediateInstruction](../../../figs/bitfield/svg/Introduction_32bit/ComparewithimmediateInstruction.svg)