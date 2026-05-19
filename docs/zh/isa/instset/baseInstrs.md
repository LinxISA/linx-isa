# 基础指令集

基础指令集是灵犀指令集中用于处理通用运算的指令的最小集合，它包含的指令长度统一为32位，并且可用于不同类型的块指令块体中。

基础指令集不仅提供了通用处理器运行所需要的一系列基础功能，其中包括算术运算、比较、比特位操作、地址计算、立即数加载以及内存访问操作等，还提供了跳转参数设置指令用于完成块指令的特定跳转。具体内容如下：

## 块头指令

| 分类 | 指令 |
|-----|------|
| **块起始指令** | [BSTART](../header/BSTART.md), [XB](../header/XB.md) |
| **块结束指令** | [BSTOP](../header/BSTOP.md) |
| **块描述指令** | [B.IOR](../header/B.IOR.md), [B.IOT](../header/B.IOT.md), [B.IOD](../header/B.IOD.md), [B.TEXT](../header/B.TEXT.md), [B.CATR](../header/B.CATR.md), [B.DATR](../header/B.DATR.md), [B.HINT](../header/B.HINT.md), [B.DIM](../header/B.DIM.md) |
| **模版块指令** | [MCOPY](../header/templateblock/MCOPY.md), [MSET](../header/templateblock/MSET.md), [FENTRY](../header/templateblock/FENTRY.md), [FRET.RA](../header/templateblock/FRET.RA.md), [FEXIT](../header/templateblock/FEXIT.md), [FRET.STK](../header/templateblock/FRET.STK.md) |

## <span id="BaseI">微指令</span>

| 分类 | 指令 |
|-----|------|
| **64位运算** | [ADD](../inst/misa_g/ADD.md), [SUB](../inst/misa_g/SUB.md), [AND](../inst/misa_g/AND.md), [OR](../inst/misa_g/OR.md), [XOR](../inst/misa_g/XOR.md), [SRL](../inst/misa_g/SRL.md), [SRA](../inst/misa_g/SRA.md), [SLL](../inst/misa_g/SLL.md) |
| **带立即数·64位运算** | [ADDI](../inst/misa_g/ADDI.md), [SUBI](../inst/misa_g/SUBI.md), [ANDI](../inst/misa_g/ANDI.md), [ORI](../inst/misa_g/ORI.md), [XORI](../inst/misa_g/XORI.md), [SRLI](../inst/misa_g/SRLI.md), [SRAI](../inst/misa_g/SRAI.md), [SLLI](../inst/misa_g/SLLI.md) |
| **32位运算** | [ADDW](../inst/misa_g/ADDW.md), [SUBW](../inst/misa_g/SUBW.md), [ANDW](../inst/misa_g/ANDW.md), [ORW](../inst/misa_g/ORW.md), [XORW](../inst/misa_g/XORW.md), [SRLW](../inst/misa_g/SRLW.md), [SRAW](../inst/misa_g/SRAW.md), [SLLW](../inst/misa_g/SLLW.md) |
| **带立即数·32位运算** | [ADDIW](../inst/misa_g/ADDIW.md), [SUBIW](../inst/misa_g/SUBIW.md), [ANDIW](../inst/misa_g/ANDIW.md), [ORIW](../inst/misa_g/ORIW.md), [XORIW](../inst/misa_g/XORIW.md), [SRLIW](../inst/misa_g/SRLIW.md), [SRAIW](../inst/misa_g/SRAIW.md), [SLLIW](../inst/misa_g/SLLIW.md) |
| **比较操作** | [CMP.EQ](../inst/misa_g/CMP.EQ.md), [CMP.NE](../inst/misa_g/CMP.NE.md), [CMP.AND](../inst/misa_g/CMP.AND.md), [CMP.OR](../inst/misa_g/CMP.OR.md), [CMP.LT](../inst/misa_g/CMP.LT.md), [CMP.GE](../inst/misa_g/CMP.GE.md), [CMP.LTU](../inst/misa_g/CMP.LTU.md), [CMP.GEU](../inst/misa_g/CMP.GEU.md) |
| **带立即数·比较操作** | [CMP.EQI](../inst/misa_g/CMP.EQI.md), [CMP.NEI](../inst/misa_g/CMP.NEI.md), [CMP.ANDI](../inst/misa_g/CMP.ANDI.md), [CMP.ORI](../inst/misa_g/CMP.ORI.md), [CMP.LTI](../inst/misa_g/CMP.LTI.md), [CMP.GEI](../inst/misa_g/CMP.GEI.md), [CMP.LTUI](../inst/misa_g/CMP.LTUI.md), [CMP.GEUI](../inst/misa_g/CMP.GEUI.md) |
| **跳转参数设置** | [SETC.EQ](../inst/misa_g/SETC.EQ.md), [SETC.NE](../inst/misa_g/SETC.NE.md), [SETC.AND](../inst/misa_g/SETC.AND.md), [SETC.OR](../inst/misa_g/SETC.OR.md), [SETC.LT](../inst/misa_g/SETC.LT.md), [SETC.GE](../inst/misa_g/SETC.GE.md), [SETC.LTU](../inst/misa_g/SETC.LTU.md), [SETC.GEU](../inst/misa_g/SETC.GEU.md) |
| **带立即数·跳转参数设置** | [SETC.EQI](../inst/misa_g/SETC.EQI.md), [SETC.NEI](../inst/misa_g/SETC.NEI.md), [SETC.ANDI](../inst/misa_g/SETC.ANDI.md), [SETC.ORI](../inst/misa_g/SETC.ORI.md), [SETC.LTI](../inst/misa_g/SETC.LTI.md), [SETC.GEI](../inst/misa_g/SETC.GEI.md), [SETC.LTUI](../inst/misa_g/SETC.LTUI.md), [SETC.GEUI](../inst/misa_g/SETC.GEUI.md) |
| **地址计算** | [ADDTPC](../inst/misa_g/ADDTPC.md), [SETRET](../inst/misa_g/SETRET.md) |
| **高位立即数加载** | [LUI](../inst/misa_g/LUI.md) |
| **乘法运算** | [MUL](../inst/misa_g/MUL.md), [MULU](../inst/misa_g/MULU.md), [MULW](../inst/misa_g/MULW.md), [MULUW](../inst/misa_g/MULUW.md), [MADD](../inst/misa_g/MADD.md), [MADDW](../inst/misa_g/MADDW.md) |
| **比特位操作** | [BXS](../inst/misa_g/BXS.md), [BXU](../inst/misa_g/BXU.md), [BIS](../inst/misa_g/BIS.md), [BIC](../inst/misa_g/BIC.md), [CTZ](../inst/misa_g/CTZ.md), [CLZ](../inst/misa_g/CLZ.md), [BCNT](../inst/misa_g/BCNT.md), [REV](../inst/misa_g/REV.md) |
| **内存加载·寄存器偏移** | [LB](../inst/misa_g/LB.md), [LH](../inst/misa_g/LH.md), [LW](../inst/misa_g/LW.md), [LD](../inst/misa_g/LD.md), [LBU](../inst/misa_g/LBU.md), [LHU](../inst/misa_g/LHU.md), [LWU](../inst/misa_g/LWU.md) |
| **内存加载·立即数偏移** | [LBI](../inst/misa_g/LBI.md), [LHI](../inst/misa_g/LHI.md), [LWI](../inst/misa_g/LWI.md), [LDI](../inst/misa_g/LDI.md), [LBUI](../inst/misa_g/LBUI.md), [LHUI](../inst/misa_g/LHUI.md), [LWUI](../inst/misa_g/LWUI.md)<br>[LHI.U](../inst/misa_g/LHI.U.md), [LWI.U](../inst/misa_g/LWI.U.md), [LDI.U](../inst/misa_g/LDI.U.md), [LHUI.U](../inst/misa_g/LHUI.U.md), [LWUI.U](../inst/misa_g/LWUI.U.md) |
| **内存加载·PC相对寻址** | [LB.PCR](../inst/misa_g/LB.PCR.md), [LH.PCR](../inst/misa_g/LH.PCR.md), [LW.PCR](../inst/misa_g/LW.PCR.md), [LD.PCR](../inst/misa_g/LD.PCR.md), [LBU.PCR](../inst/misa_g/LBU.PCR.md), [LHU.PCR](../inst/misa_g/LHU.PCR.md), [LWU.PCR](../inst/misa_g/LWU.PCR.md) |
| **内存存储·寄存器偏移** | [SB](../inst/misa_g/SB.md), [SH](../inst/misa_g/SH.md), [SW](../inst/misa_g/SW.md), [SD](../inst/misa_g/SD.md), [SH.U](../inst/misa_g/SH.U.md), [SW.U](../inst/misa_g/SW.U.md), [SD.U](../inst/misa_g/SD.U.md) |
| **内存存储·立即数偏移** | [SBI](../inst/misa_g/SBI.md), [SHI](../inst/misa_g/SHI.md), [SWI](../inst/misa_g/SWI.md), [SDI](../inst/misa_g/SDI.md), [SHI.U](../inst/misa_g/SHI.U.md), [SWI.U](../inst/misa_g/SWI.U.md), [SDI.U](../inst/misa_g/SDI.U.md) |
| **内存存储·PC相对寻址** | [SB.PCR](../inst/misa_g/SB.PCR.md), [SH.PCR](../inst/misa_g/SH.PCR.md), [SW.PCR](../inst/misa_g/SW.PCR.md), [SD.PCR](../inst/misa_g/SD.PCR.md) |
| **系统寄存器访问** | [SSRGET](../inst/misa_g/SSRGET.md), [SSRSET](../inst/misa_g/SSRSET.md), [SSRSWAP](../inst/misa_g/SSRSWAP.md), [LSRGET](../inst/misa_g/LSRGET.md), [SETC.TGT](../inst/misa_g/SETC.TGT.md) |
