# 比较类指令

该部分指令用于数据比较和置位，支持有符号，无符号比较以及寄存器-寄存器，寄存器-立即数之间的比较业务。

两输入分别为寄存器和寄存器的指令，可以有选择的先对右源寄存器截取低位有或无符号扩展，逻辑比较类（setc.and和setc.or）指令可以对右源寄存器取反，然后再进行比较。

**寄存器-寄存器比较**

|     微指令    |             汇编格式       |     描述                                    |
|---------------|----------------------------|-------------------------------------------|
| CMP.EQ   | cmp.eq SrcL, SrcR<{.sw, .uw}>, ->{t,u,Rd}   | 等于比较 |
| CMP.NE   | cmp.ne SrcL, SrcR<{.sw, .uw}>, ->{t,u,Rd}   | 不等于比较 |
| CMP.AND   | cmp.and SrcL, SrcR<{.sw, .uw, .not}>, ->{t,u,Rd}   | 相与比较 |
| CMP.OR   | cmp.or SrcL, SrcR<{.sw, .uw, .not}>, ->{t,u,Rd}   | 相或比较 |
| CMP.LT   | cmp.lt SrcL, SrcR<{.sw, .uw}>, ->{t,u,Rd}   | 有符号小于比较 |
| CMP.GE   | cmp.ge SrcL, SrcR<{.sw, .uw}>, ->{t,u,Rd}   | 有符号大于等于比较 |
| CMP.LTU  | cmp.ltu SrcL, SrcR<{.sw, .uw}>, ->{t,u,Rd}  | 无符号小于比较 |
| CMP.GEU  | cmp.geu SrcL, SrcR<{.sw, .uw}>, ->{t,u,Rd}  | 无符号大于等于比较 |

编码格式如下：

![CompareInstruction](../../../figs/bitfield/svg/Introduction_32bit/CompareInstruction.svg)

**寄存器-立即数比较**

|     微指令    |             汇编格式       |     描述                                    |
|---------------|----------------------------|-------------------------------------------|
| CMP.EQI  | cmp.eqi SrcL, simm, ->{t,u,Rd}   | 有符号立即数等于比较 |
| CMP.NEI  | cmp.nei SrcL, simm, ->{t,u,Rd}   | 有符号立即数不等于比较 |
| CMP.ANDI  | cmp.andi SrcL, simm, ->{t,u,Rd}   | 有符号立即数相与比较 |
| CMP.ORI  | cmp.ori SrcL, simm, ->{t,u,Rd}   | 有符号立即数相或比较 |
| CMP.LTI  | cmp.lti SrcL, simm, ->{t,u,Rd}   | 有符号立即数小于比较 |
| CMP.GEI  | cmp.gei SrcL, simm, ->{t,u,Rd}   | 有符号立即数大于等于比较 |
| CMP.LTUI | cmp.ltui SrcL, uimm, ->{t,u,Rd}  | 无符号立即数小于比较 |
| CMP.GEUI | cmp.geui SrcL, uimm, ->{t,u,Rd} | 无符号立即数大于等于比较 |

![ComparewithimmediateInstruction](../../../figs/bitfield/svg/Introduction_32bit/ComparewithimmediateInstruction.svg)
