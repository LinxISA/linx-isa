# 超长指令扩展

超长指令扩展的指令统一使用64位长度进行编码，这些指令通常用于特殊块类型的块体中（例如当前版本的并行块指令），实现大规模并行运算。

## 块头指令

超长指令扩展中仅包含一条块头指令[L.BSTART](../header/L.BSTART.md)。

## <span id="LongI">块体指令</span>

## **标量指令**

| 分类 | 指令 |
|-----|------|
| **长立即数加载** | [L.ADDLI](../inst/misa_l/L.ADDLI.md) |
| **内存加载·PC相对寻址** | [L.LB.PCR](../inst/misa_l/L.LB.PCR.md), [L.LH.PCR](../inst/misa_l/L.LH.PCR.md), [L.LW.PCR](../inst/misa_l/L.LW.PCR.md), [L.LD.PCR](../inst/misa_l/L.LD.PCR.md), [L.LBU.PCR](../inst/misa_l/L.LBU.PCR.md), [L.LHU.PCR](../inst/misa_l/L.LHU.PCR.md), [L.LWU.PCR](../inst/misa_l/L.LWU.PCR.md) |
| **内存存储·PC相对寻址** | [L.SB.PCR](../inst/misa_l/L.SB.PCR.md), [L.SH.PCR](../inst/misa_l/L.SH.PCR.md), [L.SW.PCR](../inst/misa_l/L.SW.PCR.md), [L.SD.PCR](../inst/misa_l/L.SD.PCR.md) |
| **原子双元素比较交换** | [L.CASBP](../inst/misa_l/L.CASBP.md), [L.CASHP](../inst/misa_l/L.CASHP.md), [L.CASWP](../inst/misa_l/L.CASWP.md), [L.CASDP](../inst/misa_l/L.CASDP.md) |
| **整数运算** | [L.ADD](../inst/misa_l/L.ADD.md), [L.SUB](../inst/misa_l/L.SUB.md), [L.AND](../inst/misa_l/L.AND.md), [L.OR](../inst/misa_l/L.OR.md), [L.XOR](../inst/misa_l/L.XOR.md), [L.SRL](../inst/misa_l/L.SRL.md), [L.SRA](../inst/misa_l/L.SRA.md), [L.SLL](../inst/misa_l/L.SLL.md) |
| **带立即数·整数运算** | [L.ADDI](../inst/misa_l/L.ADDI.md), [L.SUBI](../inst/misa_l/L.SUBI.md), [L.ANDI](../inst/misa_l/L.ANDI.md), [L.ORI](../inst/misa_l/L.ORI.md), [L.XORI](../inst/misa_l/L.XORI.md), [L.SRLI](../inst/misa_l/L.SRLI.md), [L.SRAI](../inst/misa_l/L.SRAI.md), [L.SLLI](../inst/misa_l/L.SLLI.md) |
| **比较操作** | [L.CMP.EQ](../inst/misa_l/L.CMP.EQ.md), [L.CMP.NE](../inst/misa_l/L.CMP.NE.md), [L.CMP.AND](../inst/misa_l/L.CMP.AND.md), [L.CMP.OR](../inst/misa_l/L.CMP.OR.md), [L.CMP.LT](../inst/misa_l/L.CMP.LT.md), [L.CMP.GE](../inst/misa_l/L.CMP.GE.md), [L.CMP.LTU](../inst/misa_l/L.CMP.LTU.md), [L.CMP.GEU](../inst/misa_l/L.CMP.GEU.md) |
| **带立即数·比较操作** | [L.CMP.EQI](../inst/misa_l/L.CMP.EQI.md), [L.CMP.NEI](../inst/misa_l/L.CMP.NEI.md), [L.CMP.ANDI](../inst/misa_l/L.CMP.ANDI.md), [L.CMP.ORI](../inst/misa_l/L.CMP.ORI.md), [L.CMP.LTI](../inst/misa_l/L.CMP.LTI.md), [L.CMP.GEI](../inst/misa_l/L.CMP.GEI.md), [L.CMP.LTUI](../inst/misa_l/L.CMP.LTUI.md), [L.CMP.GEUI](../inst/misa_l/L.CMP.GEUI.md) |
| **条件选择** | [L.CSEL](../inst/misa_l/L.CSEL.md) |
| **乘法运算** | [L.MUL](../inst/misa_l/L.MUL.md), [L.MADD](../inst/misa_l/L.MADD.md) |
| **比特位操作** | [L.BXS](../inst/misa_l/L.BXS.md), [L.BXU](../inst/misa_l/L.BXU.md), [L.BIS](../inst/misa_l/L.BIS.md), [L.BIC](../inst/misa_l/L.BIC.md), [L.BCNT](../inst/misa_l/L.BCNT.md), [L.REV](../inst/misa_l/L.REV.md) |
| **内存加载·寄存器偏移** | [L.LB](../inst/misa_l/L.LB.md), [L.LH](../inst/misa_l/L.LH.md), [L.LW](../inst/misa_l/L.LW.md), [L.LD](../inst/misa_l/L.LD.md), [L.LBU](../inst/misa_l/L.LBU.md), [L.LHU](../inst/misa_l/L.LHU.md), [L.LWU](../inst/misa_l/L.LWU.md) |
| **内存加载·立即数偏移** | [L.LBI](../inst/misa_l/L.LB.md), [L.LHI](../inst/misa_l/L.LH.md), [L.LWI](../inst/misa_l/L.LW.md), [L.LDI](../inst/misa_l/L.LD.md), [L.LBUI](../inst/misa_l/L.LBU.md), [L.LHUI](../inst/misa_l/L.LHU.md), [L.LWUI](../inst/misa_l/L.LWU.md)<br>[L.LHI.U](../inst/misa_l/L.LH.md), [L.LWI.U](../inst/misa_l/L.LW.md), [L.LDI.U](../inst/misa_l/L.LD.md), [L.LHUI.U](../inst/misa_l/L.LHU.md), [L.LWUI.U](../inst/misa_l/L.LWU.md) |
| **内存存储·寄存器偏移** | [L.SB](../inst/misa_l/L.SB.md), [L.SH](../inst/misa_l/L.SH.md), [L.SW](../inst/misa_l/L.SW.md), [L.SD](../inst/misa_l/L.SD.md), [L.SH.U](../inst/misa_l/L.SH.U.md), [L.SW.U](../inst/misa_l/L.SW.U.md), [L.SD.U](../inst/misa_l/L.SD.U.md) |
| **内存存储·立即数偏移** | [L.SBI](../inst/misa_l/L.SBI.md), [L.SHI](../inst/misa_l/L.SHI.md), [L.SWI](../inst/misa_l/L.SWI.md), [L.SDI](../inst/misa_l/L.SDI.md), [L.SHI.U](../inst/misa_l/L.SHI.U.md), [L.SWI.U](../inst/misa_l/L.SWI.U.md), [L.SDI.U](../inst/misa_l/L.SDI.U.md) |
| **原子操作·加载字** | [L.LW.ADD](../inst/misa_l/L.LW.ADD.md), [L.LW.AND](../inst/misa_l/L.LW.AND.md), [L.LW.OR](../inst/misa_l/L.LW.OR.md), [L.LW.XOR](../inst/misa_l/L.LW.XOR.md), [L.LW.MAX](../inst/misa_l/L.LW.MAX.md), [L.LW.MIN](../inst/misa_l/L.LW.MIN.md) |
| **原子操作·加载双字** | [L.LD.ADD](../inst/misa_l/L.LD.ADD.md), [L.LD.AND](../inst/misa_l/L.LD.AND.md), [L.LD.OR](../inst/misa_l/L.LD.OR.md), [L.LD.XOR](../inst/misa_l/L.LD.XOR.md), [L.LD.MAX](../inst/misa_l/L.LD.MAX.md), [L.LD.MIN](../inst/misa_l/L.LD.MIN.md) |
| **原子操作·存储字** | [L.SW.ADD](../inst/misa_l/L.SW.ADD.md), [L.SW.AND](../inst/misa_l/L.SW.AND.md), [L.SW.OR](../inst/misa_l/L.SW.OR.md), [L.SW.XOR](../inst/misa_l/L.SW.XOR.md), [L.SW.MAX](../inst/misa_l/L.SW.MAX.md), [L.SW.MIN](../inst/misa_l/L.SW.MIN.md), [L.SW.MAX](../inst/misa_l/L.SW.MAX.md), [L.SW.MIN](../inst/misa_l/L.SW.MIN.md) |
| **原子操作·存储双字** | [L.SD.ADD](../inst/misa_l/L.SD.ADD.md), [L.SD.AND](../inst/misa_l/L.SD.AND.md), [L.SD.OR](../inst/misa_l/L.SD.OR.md), [L.SD.XOR](../inst/misa_l/L.SD.XOR.md), [L.SD.MAX](../inst/misa_l/L.SD.MAX.md), [L.SD.MIN](../inst/misa_l/L.SD.MIN.md), [L.SD.MAX](../inst/misa_l/L.SD.MAX.md),  [L.SD.MIN](../inst/misa_l/L.SD.MIN.md) |
| **浮点运算** | [L.FADD](../inst/misa_l/L.FADD.md), [L.FSUB](../inst/misa_l/L.FSUB.md), [L.FMUL](../inst/misa_l/L.FMUL.md), [L.FDIV](../inst/misa_l/L.FDIV.md), [L.FMADD](../inst/misa_l/L.FMADD.md), [L.FMSUB](../inst/misa_l/L.FMSUB.md), [L.FNMADD](../inst/misa_l/L.FNMADD.md), [L.FNMSUB](../inst/misa_l/L.FNMSUB.md) |
| **浮点比较** | [L.FEQ](../inst/misa_l/L.FEQ.md), [L.FNE](../inst/misa_l/L.FNE.md), [L.FLT](../inst/misa_l/L.FLT.md), [L.FGE](../inst/misa_l/L.FGE.md), [L.FEQS](../inst/misa_l/L.FEQS.md), [L.FNES](../inst/misa_l/L.FNES.md), [L.FLTS](../inst/misa_l/L.FLTS.md), [L.FGES](../inst/misa_l/L.FGES.md) |
| **最大最小值** | [L.MAX](../inst/misa_l/L.MAX.md), [L.MIN](../inst/misa_l/L.MIN.md), [L.FMAX](../inst/misa_l/L.FMAX.md), [L.FMIN](../inst/misa_l/L.FMIN.md) |
| **数据格式转换** | [L.FCVT](../inst/misa_l/L.FCVT.md), [L.FCVTI](../inst/misa_l/L.FCVTI.md), [L.ICVT](../inst/misa_l/L.ICVT.md), [L.ICVTF](../inst/misa_l/L.ICVTF.md) |
| **浮点特殊运算** | [L.FABS](../inst/misa_l/L.FABS.md), [L.FSQRT](../inst/misa_l/L.FSQRT.md), [L.FEXP](../inst/misa_l/L.FEXP.md), [L.FRECIP](../inst/misa_l/L.FRECIP.md), [L.FCLASS](../inst/misa_l/L.FCLASS.md) |
| **通用队列管理** | [L.QPUSH](../inst/misa_l/L.QPUSH.md), [L.QPOP](../inst/misa_l/L.QPOP.md) |

### **向量指令**

| 分类 | 指令 |
|-----|------|
| **整数运算** | [V.ADD](../inst/misa_v/V.ADD.md), [V.SUB](../inst/misa_v/V.SUB.md), [V.AND](../inst/misa_v/V.AND.md), [V.OR](../inst/misa_v/V.OR.md), [V.XOR](../inst/misa_v/V.XOR.md), [V.SRL](../inst/misa_v/V.SRL.md), [V.SRA](../inst/misa_v/V.SRA.md), [V.SLL](../inst/misa_v/V.SLL.md) |
| **带立即数·整数运算** | [V.ADDI](../inst/misa_v/V.ADDI.md), [V.SUBI](../inst/misa_v/V.SUBI.md), [V.ANDI](../inst/misa_v/V.ANDI.md), [V.ORI](../inst/misa_v/V.ORI.md), [V.XORI](../inst/misa_v/V.XORI.md), [V.SRLI](../inst/misa_v/V.SRLI.md), [V.SRAI](../inst/misa_v/V.SRAI.md), [V.SLLI](../inst/misa_v/V.SLLI.md) |
| **比较操作** | [V.CMP.EQ](../inst/misa_v/V.CMP.EQ.md), [V.CMP.NE](../inst/misa_v/V.CMP.NE.md), [V.CMP.AND](../inst/misa_v/V.CMP.AND.md), [V.CMP.OR](../inst/misa_v/V.CMP.OR.md), [V.CMP.LT](../inst/misa_v/V.CMP.LT.md), [V.CMP.GE](../inst/misa_v/V.CMP.GE.md), [V.CMP.LTU](../inst/misa_v/V.CMP.LTU.md), [V.CMP.GEU](../inst/misa_v/V.CMP.GEU.md) |
| **带立即数·比较操作** | [V.CMP.EQI](../inst/misa_v/V.CMP.EQI.md), [V.CMP.NEI](../inst/misa_v/V.CMP.NEI.md), [V.CMP.ANDI](../inst/misa_v/V.CMP.ANDI.md), [V.CMP.ORI](../inst/misa_v/V.CMP.ORI.md), [V.CMP.LTI](../inst/misa_v/V.CMP.LTI.md), [V.CMP.GEI](../inst/misa_v/V.CMP.GEI.md), [V.CMP.LTUI](../inst/misa_v/V.CMP.LTUI.md), [V.CMP.GEUI](../inst/misa_v/V.CMP.GEUI.md) |
| **条件选择** | [V.CSEL](../inst/misa_v/V.CSEL.md) |
| **乘法运算** | [V.MUL](../inst/misa_v/V.MUL.md), [V.MADD](../inst/misa_v/V.MADD.md) |
| **比特位操作** | [V.BXS](../inst/misa_v/V.BXS.md), [V.BXU](../inst/misa_v/V.BXU.md), [V.BIS](../inst/misa_v/V.BIS.md), [V.BIC](../inst/misa_v/V.BIC.md), [V.BCNT](../inst/misa_v/V.BCNT.md), [V.REV](../inst/misa_v/V.REV.md) |
| **内存加载·寄存器偏移** | [V.LB](../inst/misa_v/V.LB.md), [V.LH](../inst/misa_v/V.LH.md), [V.LW](../inst/misa_v/V.LW.md), [V.LD](../inst/misa_v/V.LD.md), [V.LBU](../inst/misa_v/V.LBU.md), [V.LHU](../inst/misa_v/V.LHU.md), [V.LWU](../inst/misa_v/V.LWU.md) |
| **内存加载·立即数偏移** | [V.LBI](../inst/misa_v/V.LB.md), [V.LHI](../inst/misa_v/V.LH.md), [V.LWI](../inst/misa_v/V.LW.md), [V.LDI](../inst/misa_v/V.LD.md), [V.LBUI](../inst/misa_v/V.LBU.md), [V.LHUI](../inst/misa_v/V.LHU.md), [V.LWUI](../inst/misa_v/V.LWU.md)<br>[V.LHI.U](../inst/misa_v/V.LH.md), [V.LWI.U](../inst/misa_v/V.LW.md), [V.LDI.U](../inst/misa_v/V.LD.md), [V.LHUI.U](../inst/misa_v/V.LHU.md), [V.LWUI.U](../inst/misa_v/V.LWU.md) |
| **内存存储·寄存器偏移** | [V.SB](../inst/misa_v/V.SB.md), [V.SH](../inst/misa_v/V.SH.md), [V.SW](../inst/misa_v/V.SW.md), [V.SD](../inst/misa_v/V.SD.md), [V.SH.U](../inst/misa_v/V.SH.U.md), [V.SW.U](../inst/misa_v/V.SW.U.md), [V.SD.U](../inst/misa_v/V.SD.U.md) |
| **内存存储·立即数偏移** | [V.SBI](../inst/misa_v/V.SBI.md), [V.SHI](../inst/misa_v/V.SHI.md), [V.SWI](../inst/misa_v/V.SWI.md), [V.SDI](../inst/misa_v/V.SDI.md), [V.SHI.U](../inst/misa_v/V.SHI.U.md), [V.SWI.U](../inst/misa_v/V.SWI.U.md), [V.SDI.U](../inst/misa_v/V.SDI.U.md) |
| **桥接·内存加载·寄存器偏移** | [V.LB.BRG](../inst/misa_v/V.LB.BRG.md), [V.LH.BRG](../inst/misa_v/V.LH.BRG.md), [V.LW.BRG](../inst/misa_v/V.LW.BRG.md), [V.LD.BRG](../inst/misa_v/V.LD.BRG.md), [V.LBU.BRG](../inst/misa_v/V.LBU.BRG.md), [V.LHU.BRG](../inst/misa_v/V.LHU.BRG.md), [V.LWU.BRG](../inst/misa_v/V.LWU.BRG.md) |
| **桥接·内存加载·立即数偏移** | [V.LBI.BRG](../inst/misa_v/V.LB.BRG.md), [V.LHI.BRG](../inst/misa_v/V.LH.BRG.md), [V.LWI.BRG](../inst/misa_v/V.LW.BRG.md), [V.LDI.BRG](../inst/misa_v/V.LD.BRG.md), [V.LBUI.BRG](../inst/misa_v/V.LBU.BRG.md), [V.LHUI.BRG](../inst/misa_v/V.LHU.BRG.md), [V.LWUI.BRG](../inst/misa_v/V.LWU.BRG.md)<br>[V.LHI.U.BRG](../inst/misa_v/V.LH.BRG.md), [V.LWI.U.BRG](../inst/misa_v/V.LW.BRG.md), [V.LDI.U.BRG](../inst/misa_v/V.LD.BRG.md), [V.LHUI.U.BRG](../inst/misa_v/V.LHU.BRG.md), [V.LWUI.U.BRG](../inst/misa_v/V.LWU.BRG.md) |
| **桥接·内存存储·寄存器偏移** | [V.SB.BRG](../inst/misa_v/V.SB.BRG.md), [V.SH.BRG](../inst/misa_v/V.SH.BRG.md), [V.SW.BRG](../inst/misa_v/V.SW.BRG.md), [V.SD.BRG](../inst/misa_v/V.SD.BRG.md), [V.SH.U.BRG](../inst/misa_v/V.SH.UBRG.md), [V.SW.U.BRG](../inst/misa_v/V.SW.UBRG.md), [V.SD.U.BRG](../inst/misa_v/V.SD.UBRG.md) |
| **桥接·内存存储·立即数偏移** | [V.SBI.BRG](../inst/misa_v/V.SBI.BRG.md), [V.SHI.BRG](../inst/misa_v/V.SHI.BRG.md), [V.SWI.BRG](../inst/misa_v/V.SWI.BRG.md), [V.SDI.BRG](../inst/misa_v/V.SDI.BRG.md), [V.SHI.U.BRG](../inst/misa_v/V.SHI.UBRG.md), [V.SWI.U.BRG](../inst/misa_v/V.SWI.UBRG.md), [V.SDI.U.BRG](../inst/misa_v/V.SDI.UBRG.md) |
| **原子操作·加载字** | [V.LW.ADD](../inst/misa_v/V.LW.ADD.md), [V.LW.AND](../inst/misa_v/V.LW.AND.md), [V.LW.OR](../inst/misa_v/V.LW.OR.md), [V.LW.XOR](../inst/misa_v/V.LW.XOR.md), [V.LW.MAX](../inst/misa_v/V.LW.MAX.md), [V.LW.MIN](../inst/misa_v/V.LW.MIN.md) |
| **原子操作·加载双字** | [V.LD.ADD](../inst/misa_v/V.LD.ADD.md), [V.LD.AND](../inst/misa_v/V.LD.AND.md), [V.LD.OR](../inst/misa_v/V.LD.OR.md), [V.LD.XOR](../inst/misa_v/V.LD.XOR.md), [V.LD.MAX](../inst/misa_v/V.LD.MAX.md), [V.LD.MIN](../inst/misa_v/V.LD.MIN.md) |
| **原子操作·存储字** | [V.SW.ADD](../inst/misa_v/V.SW.ADD.md), [V.SW.AND](../inst/misa_v/V.SW.AND.md), [V.SW.OR](../inst/misa_v/V.SW.OR.md), [V.SW.XOR](../inst/misa_v/V.SW.XOR.md), [V.SW.MAX](../inst/misa_v/V.SW.MAX.md), [V.SW.MIN](../inst/misa_v/V.SW.MIN.md), [V.SW.MAX](../inst/misa_v/V.SW.MAX.md), [V.SW.MIN](../inst/misa_v/V.SW.MIN.md) |
| **原子操作·存储双字** | [V.SD.ADD](../inst/misa_v/V.SD.ADD.md), [V.SD.AND](../inst/misa_v/V.SD.AND.md), [V.SD.OR](../inst/misa_v/V.SD.OR.md), [V.SD.XOR](../inst/misa_v/V.SD.XOR.md), [V.SD.MAX](../inst/misa_v/V.SD.MAX.md), [V.SD.MIN](../inst/misa_v/V.SD.MIN.md), [V.SD.MAX](../inst/misa_v/V.SD.MAX.md),  [V.SD.MIN](../inst/misa_v/V.SD.MIN.md) |
| **浮点运算** | [V.FADD](../inst/misa_v/V.FADD.md), [V.FSUB](../inst/misa_v/V.FSUB.md), [V.FMUL](../inst/misa_v/V.FMUL.md), [V.FDIV](../inst/misa_v/V.FDIV.md), [V.FMADD](../inst/misa_v/V.FMADD.md), [V.FMSUB](../inst/misa_v/V.FMSUB.md), [V.FNMADD](../inst/misa_v/V.FNMADD.md), [V.FNMSUB](../inst/misa_v/V.FNMSUB.md) |
| **浮点比较** | [V.FEQ](../inst/misa_v/V.FEQ.md), [V.FNE](../inst/misa_v/V.FNE.md), [V.FLT](../inst/misa_v/V.FLT.md), [V.FGE](../inst/misa_v/V.FGE.md), [V.FEQS](../inst/misa_v/V.FEQS.md), [V.FNES](../inst/misa_v/V.FNES.md), [V.FLTS](../inst/misa_v/V.FLTS.md), [V.FGES](../inst/misa_v/V.FGES.md) |
| **最大最小值** | [V.MAX](../inst/misa_v/V.MAX.md), [V.MIN](../inst/misa_v/V.MIN.md), [V.FMAX](../inst/misa_v/V.FMAX.md), [V.FMIN](../inst/misa_v/V.FMIN.md) |
| **数据格式转换** | [V.FCVT](../inst/misa_v/V.FCVT.md), [V.FCVTI](../inst/misa_v/V.FCVTI.md), [V.ICVT](../inst/misa_v/V.ICVT.md), [V.ICVTF](../inst/misa_v/V.ICVTF.md) |
| **浮点特殊运算** | [V.FABS](../inst/misa_v/V.FABS.md), [V.FSQRT](../inst/misa_v/V.FSQRT.md), [V.FEXP](../inst/misa_v/V.FEXP.md), [V.FRECIP](../inst/misa_v/V.FRECIP.md), [V.FCLASS](../inst/misa_v/V.FCLASS.md) |
| **通用队列管理** | [V.QPUSH](../inst/misa_v/V.QPUSH.md), [V.QPOP](../inst/misa_v/V.QPOP.md) |
| **归约操作** | [V.RDADD](../inst/misa_v/V.RDADD.md), [V.RDAND](../inst/misa_v/V.RDAND.md), [V.RDOR](../inst/misa_v/V.RDOR.md), [V.RDXOR](../inst/misa_v/V.RDXOR.md), [V.RDFADD](../inst/misa_v/V.RDFADD.md), [V.RDMAX](../inst/misa_v/V.RDMAX.md), [V.RDMIN](../inst/misa_v/V.RDMIN.md), [V.RDFMAX](../inst/misa_v/V.RDFMAX.md), [V.RDFMIN](../inst/misa_v/V.RDFMIN.md) |
| **跨通道搬移** | [V.SHFL.IDX](../inst/misa_v/V.SHFL.IDX.md), [V.SHFL.BFLY](../inst/misa_v/V.SHFL.BFLY.md), [V.SHFL.UP](../inst/misa_v/V.SHFL.UP.md), [V.SHFL.DOWN](../inst/misa_v/V.SHFL.DOWN.md) |
