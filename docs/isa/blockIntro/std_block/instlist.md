# 微指令列表

灵犀指令集中，不同类型的块指令可以从每种扩展指令集中挑选部分特定的指令应用于本块块体，并不需要支持所有指令。

当前版本，整型标量块块体中提供的微指令列表如下：

## <span id="puclicinsts">公共指令列表</span>

包含所有的16bit压缩指令：

| 分类 | 指令 |
| -- | -- |
| **寄存器移动** | [C.MOVR](../../inst/misa_c/C.MOVR.md) |
| **立即数移动** | [C.MOVI](../../inst/misa_c/C.MOVI.md) | 
| **PC相对寻址** | [C.SETRET](../../inst/misa_c/C.SETRET.md) |
| **跳转参数设置** | [C.SETC.EQ](../../inst/misa_c/C.SETC.EQ.md), [C.SETC.NE](../../inst/misa_c/C.SETC.NE.md), [C.SETC.TGT](../../inst/misa_c/C.SETC.TGT.md) |
| **算术运算** | [C.ADD](../../inst/misa_c/C.ADD.md), [C.SUB](../../inst/misa_c/C.SUB.md), [C.AND](../../inst/misa_c/C.AND.md), [C.OR](../../inst/misa_c/C.OR.md) |
| **带立即数·算术运算** | [C.ADDI](../../inst/misa_c/C.ADDI.md) |
| **内存访问** | [C.LWI](../../inst/misa_c/C.LWI.md), [C.LDI](../../inst/misa_c/C.LDI.md), [C.SWI](../../inst/misa_c/C.SWI.md), [C.SDI](../../inst/misa_c/C.SDI.md) |
| **低位扩展** | [C.SEXT.B](../../inst/misa_c/C.SEXT.B.md), [C.SEXT.H](../../inst/misa_c/C.SEXT.H.md), [C.SEXT.W](../../inst/misa_c/C.SEXT.W.md), [C.ZEXT.B](../../inst/misa_c/C.ZEXT.B.md), [C.ZEXT.H](../../inst/misa_c/C.ZEXT.H.md), [C.ZEXT.W](../../inst/misa_c/C.ZEXT.W.md) |
| **带立即数·比较** | [C.CMP.EQI](../../inst/misa_c/C.CMP.EQI.md), [C.CMP.NEI](../../inst/misa_c/C.CMP.NEI.md) |
| **移位操作** | [C.SLLI](../../inst/misa_c/C.SLLI.md), [C.SRLI](../../inst/misa_c/C.SRLI.md) |
| **系统寄存器访问** | [C.SSRGET](../../inst/misa_c/C.SSRGET.md) |

包含的32bit指令如下：

| 分类 | 指令 |
|-----|------|
| **64位运算** | [ADD](../../inst/misa_g/ADD.md), [SUB](../../inst/misa_g/SUB.md), [AND](../../inst/misa_g/AND.md), [OR](../../inst/misa_g/OR.md), [XOR](../../inst/misa_g/XOR.md), [SRL](../../inst/misa_g/SRL.md), [SRA](../../inst/misa_g/SRA.md), [SLL](../../inst/misa_g/SLL.md) |
| **带立即数·64位运算** | [ADDI](../../inst/misa_g/ADDI.md), [SUBI](../../inst/misa_g/SUBI.md), [ANDI](../../inst/misa_g/ANDI.md), [ORI](../../inst/misa_g/ORI.md), [XORI](../../inst/misa_g/XORI.md), [SRLI](../../inst/misa_g/SRLI.md), [SRAI](../../inst/misa_g/SRAI.md), [SLLI](../../inst/misa_g/SLLI.md) |
| **32位运算** | [ADDW](../../inst/misa_g/ADDW.md), [SUBW](../../inst/misa_g/SUBW.md), [ANDW](../../inst/misa_g/ANDW.md), [ORW](../../inst/misa_g/ORW.md), [XORW](../../inst/misa_g/XORW.md), [SRLW](../../inst/misa_g/SRLW.md), [SRAW](../../inst/misa_g/SRAW.md), [SLLW](../../inst/misa_g/SLLW.md) |
| **带立即数·32位运算** | [ADDIW](../../inst/misa_g/ADDIW.md), [SUBIW](../../inst/misa_g/SUBIW.md), [ANDIW](../../inst/misa_g/ANDIW.md), [ORIW](../../inst/misa_g/ORIW.md), [XORIW](../../inst/misa_g/XORIW.md), [SRLIW](../../inst/misa_g/SRLIW.md), [SRAIW](../../inst/misa_g/SRAIW.md), [SLLIW](../../inst/misa_g/SLLIW.md) |
| **比较操作** | [CMP.EQ](../../inst/misa_g/CMP.EQ.md), [CMP.NE](../../inst/misa_g/CMP.NE.md), [CMP.AND](../../inst/misa_g/CMP.AND.md), [CMP.OR](../../inst/misa_g/CMP.OR.md), [CMP.LT](../../inst/misa_g/CMP.LT.md), [CMP.GE](../../inst/misa_g/CMP.GE.md), [CMP.LTU](../../inst/misa_g/CMP.LTU.md), [CMP.GEU](../../inst/misa_g/CMP.GEU.md) |
| **带立即数·比较操作** | [CMP.EQI](../../inst/misa_g/CMP.EQI.md), [CMP.NEI](../../inst/misa_g/CMP.NEI.md), [CMP.ANDI](../../inst/misa_g/CMP.ANDI.md), [CMP.ORI](../../inst/misa_g/CMP.ORI.md), [CMP.LTI](../../inst/misa_g/CMP.LTI.md), [CMP.GEI](../../inst/misa_g/CMP.GEI.md), [CMP.LTUI](../../inst/misa_g/CMP.LTUI.md), [CMP.GEUI](../../inst/misa_g/CMP.GEUI.md) |
| **跳转参数设置** | [SETC.EQ](../../inst/misa_g/SETC.EQ.md), [SETC.NE](../../inst/misa_g/SETC.NE.md), [SETC.AND](../../inst/misa_g/SETC.AND.md), [SETC.OR](../../inst/misa_g/SETC.OR.md), [SETC.LT](../../inst/misa_g/SETC.LT.md), [SETC.GE](../../inst/misa_g/SETC.GE.md), [SETC.LTU](../../inst/misa_g/SETC.LTU.md), [SETC.GEU](../../inst/misa_g/SETC.GEU.md) |
| **带立即数·跳转参数设置** | [SETC.EQI](../../inst/misa_g/SETC.EQI.md), [SETC.NEI](../../inst/misa_g/SETC.NEI.md), [SETC.ANDI](../../inst/misa_g/SETC.ANDI.md), [SETC.ORI](../../inst/misa_g/SETC.ORI.md), [SETC.LTI](../../inst/misa_g/SETC.LTI.md), [SETC.GEI](../../inst/misa_g/SETC.GEI.md), [SETC.LTUI](../../inst/misa_g/SETC.LTUI.md), [SETC.GEUI](../../inst/misa_g/SETC.GEUI.md) |
| **地址计算** | [ADDTPC](../../inst/misa_g/ADDTPC.md), [SETRET](../../inst/misa_g/SETRET.md) |
| **高位立即数加载** | [LUI](../../inst/misa_g/LUI.md) |
| **乘法运算** | [MUL](../../inst/misa_g/MUL.md), [MULU](../../inst/misa_g/MULU.md), [MULW](../../inst/misa_g/MULW.md), [MULUW](../../inst/misa_g/MULUW.md), [MADD](../../inst/misa_g/MADD.md), [MADDW](../../inst/misa_g/MADDW.md) |
| **除法操作** | [DIV](../../inst/misa_g/DIV.md), [DIVU](../../inst/misa_g/DIVU.md), [DIVW](../../inst/misa_g/DIVW.md), [DIVUW](../../inst/misa_g/DIVUW.md) |
| **求余操作** | [REM](../../inst/misa_g/REM.md), [REMU](../../inst/misa_g/REMU.md), [REMW](../../inst/misa_g/REMW.md), [REMUW](../../inst/misa_g/REMUW.md) |
| **条件选择** | [CSEL](../../inst/misa_g/CSEL.md) |
| **比特位操作** | [BXS](../../inst/misa_g/BXS.md), [BXU](../../inst/misa_g/BXU.md), [BIS](../../inst/misa_g/BIS.md), [BIC](../../inst/misa_g/BIC.md), [CTZ](../../inst/misa_g/CTZ.md), [CLZ](../../inst/misa_g/CLZ.md), [BCNT](../../inst/misa_g/BCNT.md), [REV](../../inst/misa_g/REV.md) |
| **内存加载·寄存器偏移** | [LB](../../inst/misa_g/LB.md), [LH](../../inst/misa_g/LH.md), [LW](../../inst/misa_g/LW.md), [LD](../../inst/misa_g/LD.md), [LBU](../../inst/misa_g/LBU.md), [LHU](../../inst/misa_g/LHU.md), [LWU](../../inst/misa_g/LWU.md) |
| **内存加载·立即数偏移** | [LBI](../../inst/misa_g/LBI.md), [LHI](../../inst/misa_g/LHI.md), [LWI](../../inst/misa_g/LWI.md), [LDI](../../inst/misa_g/LDI.md), [LBUI](../../inst/misa_g/LBUI.md), [LHUI](../../inst/misa_g/LHUI.md), [LWUI](../../inst/misa_g/LWUI.md)<br>[LHI.U](../../inst/misa_g/LHI.U.md), [LWI.U](../../inst/misa_g/LWI.U.md), [LDI.U](../../inst/misa_g/LDI.U.md), [LHUI.U](../../inst/misa_g/LHUI.U.md), [LWUI.U](../../inst/misa_g/LWUI.U.md) |
| **内存加载·PC相对寻址** | [LB.PCR](../../inst/misa_g/LB.PCR.md), [LH.PCR](../../inst/misa_g/LH.PCR.md), [LW.PCR](../../inst/misa_g/LW.PCR.md), [LD.PCR](../../inst/misa_g/LD.PCR.md), [LBU.PCR](../../inst/misa_g/LBU.PCR.md), [LHU.PCR](../../inst/misa_g/LHU.PCR.md), [LWU.PCR](../../inst/misa_g/LWU.PCR.md) |
| **内存存储·寄存器偏移** | [SB](../../inst/misa_g/SB.md), [SH](../../inst/misa_g/SH.md), [SW](../../inst/misa_g/SW.md), [SD](../../inst/misa_g/SD.md), [SH.U](../../inst/misa_g/SH.U.md), [SW.U](../../inst/misa_g/SW.U.md), [SD.U](../../inst/misa_g/SD.U.md) |
| **内存存储·立即数偏移** | [SBI](../../inst/misa_g/SBI.md), [SHI](../../inst/misa_g/SHI.md), [SWI](../../inst/misa_g/SWI.md), [SDI](../../inst/misa_g/SDI.md), [SHI.U](../../inst/misa_g/SHI.U.md), [SWI.U](../../inst/misa_g/SWI.U.md), [SDI.U](../../inst/misa_g/SDI.U.md) |
| **内存存储·PC相对寻址** | [SB.PCR](../../inst/misa_g/SB.PCR.md), [SH.PCR](../../inst/misa_g/SH.PCR.md), [SW.PCR](../../inst/misa_g/SW.PCR.md), [SD.PCR](../../inst/misa_g/SD.PCR.md) |
| **系统寄存器访问** | [SSRGET](../../inst/misa_g/SSRGET.md), [SSRSET](../../inst/misa_g/SSRSET.md), [SSRSWAP](../../inst/misa_g/SSRSWAP.md), [LSRGET](../../inst/misa_g/LSRGET.md), [SETC.TGT](../../inst/misa_g/SETC.TGT.md) |

包含的48bit指令如下：

| 分类 | 指令 |
|-----|------|
| **带立即数·64位运算** | [HL.ADDI](../../inst/misa_h/HL.ADDI.md), [HL.SUBI](../../inst/misa_h/HL.SUBI.md), [HL.ANDI](../../inst/misa_h/HL.ANDI.md), [HL.ORI](../../inst/misa_h/HL.ORI.md), [HL.XORI](../../inst/misa_h/HL.XORI.md) |
| **带立即数·32位运算** | [HL.ADDIW](../../inst/misa_h/HL.ADDIW.md), [HL.SUBIW](../../inst/misa_h/HL.SUBIW.md), [HL.ANDIW](../../inst/misa_h/HL.ANDIW.md), [HL.ORIW](../../inst/misa_h/HL.ORIW.md), [HL.XORIW](../../inst/misa_h/HL.XORIW.md) |
| **带立即数·比较操作** | [HL.CMP.EQI](../../inst/misa_h/HL.CMP.EQI.md), [HL.CMP.NEI](../../inst/misa_h/HL.CMP.NEI.md), [HL.CMP.ANDI](../../inst/misa_h/HL.CMP.ANDI.md), [HL.CMP.ORI](../../inst/misa_h/HL.CMP.ORI.md), [HL.CMP.LTI](../../inst/misa_h/HL.CMP.LTI.md), [HL.CMP.GEI](../../inst/misa_h/HL.CMP.GEI.md), [HL.CMP.LTUI](../../inst/misa_h/HL.CMP.LTUI.md), [HL.CMP.GEUI](../../inst/misa_h/HL.CMP.GEUI.md) |
| **带立即数·跳转参数设置** | [HL.SETC.EQI](../../inst/misa_h/HL.SETC.EQI.md), [HL.SETC.NEI](../../inst/misa_h/HL.SETC.NEI.md), [HL.SETC.ANDI](../../inst/misa_h/HL.SETC.ANDI.md), [HL.SETC.ORI](../../inst/misa_h/HL.SETC.ORI.md), [HL.SETC.LTI](../../inst/misa_h/HL.SETC.LTI.md), [HL.SETC.GEI](../../inst/misa_h/HL.SETC.GEI.md), [HL.SETC.LTUI](../../inst/misa_h/HL.SETC.LTUI.md), [HL.SETC.GEUI](../../inst/misa_h/HL.SETC.GEUI.md) |
| **地址计算** | [HL.ADDTPC](../../inst/misa_h/HL.ADDTPC.md), [HL.SETRET](../../inst/misa_h/HL.SETRET.md) |
| **长立即数加载** | [HL.LIS](../../inst/misa_h/HL.LIS.md), [HL.LIU](../../inst/misa_h/HL.LIU.md), [HL.LUI](../../inst/misa_h/HL.LUI.md) |
| **乘法操作** | [HL.MUL](../../inst/misa_h/HL.MUL.md), [HL.MULU](../../inst/misa_h/HL.MULU.md), [HL.MADD](../../inst/misa_h/HL.MADD.md), [HL.MADDW](../../inst/misa_h/HL.MADDW.md) |
| **除法操作** | [HL.DIV](../../inst/misa_h/HL.DIV.md), [HL.DIVU](../../inst/misa_h/HL.DIVU.md), [HL.DIVW](../../inst/misa_h/HL.DIVW.md), [HL.DIVUW](../../inst/misa_h/HL.DIVUW.md) |
| **求余操作** | [HL.REM](../../inst/misa_h/HL.REM.md), [HL.REMU](../../inst/misa_h/HL.REMU.md), [HL.REMW](../../inst/misa_h/HL.REMW.md), [HL.REMUW](../../inst/misa_h/HL.REMUW.md) |
| **内存加载·立即数偏移** | [HL.LBI](../../inst/misa_h/HL.LBI.md), [HL.LHI](../../inst/misa_h/HL.LHI.md), [HL.LWI](../../inst/misa_h/HL.LWI.md), [HL.LDI](../../inst/misa_h/HL.LDI.md), [HL.LBUI](../../inst/misa_h/HL.LBUI.md), [HL.LHUI](../../inst/misa_h/HL.LHUI.md), [HL.LWUI](../../inst/misa_h/HL.LWUI.md)<br>[HL.LHI.U](../../inst/misa_h/HL.LHI.U.md), [HL.LWI.U](../../inst/misa_h/HL.LWI.U.md), [HL.LDI.U](../../inst/misa_h/HL.LDI.U.md), [HL.LHUI.U](../../inst/misa_h/HL.LHUI.U.md), [HL.LWUI.U](../../inst/misa_h/HL.LWUI.U.md) |
| **内存对加载·寄存器偏移** | [HL.LBP](../../inst/misa_h/HL.LBP.md), [HL.LHP](../../inst/misa_h/HL.LHP.md), [HL.LWP](../../inst/misa_h/HL.LWP.md), [HL.LDP](../../inst/misa_h/HL.LDP.md), [HL.LBUP](../../inst/misa_h/HL.LBUP.md), [HL.LHUP](../../inst/misa_h/HL.LHUP.md), [HL.LWUP](../../inst/misa_h/HL.LWUP.md) |
| **内存对加载·立即数偏移** | [HL.LBIP](../../inst/misa_h/HL.LBIP.md), [HL.LHIP](../../inst/misa_h/HL.LHIP.md), [HL.LWIP](../../inst/misa_h/HL.LWIP.md), [HL.LDIP](../../inst/misa_h/HL.LDIP.md), [HL.LBUIP](../../inst/misa_h/HL.LBUIP.md), [HL.LHUIP](../../inst/misa_h/HL.LHUIP.md), [HL.LWUIP](../../inst/misa_h/HL.LWUIP.md)<br>[HL.LHIP.U](../../inst/misa_h/HL.LHIP.U.md), [HL.LWIP.U](../../inst/misa_h/HL.LWIP.U.md), [HL.LDIP.U](../../inst/misa_h/HL.LDIP.U.md), [HL.LHUIP.U](../../inst/misa_h/HL.LHUIP.U.md), [HL.LWUIP.U](../../inst/misa_h/HL.LWUIP.U.md) |
| **内存加载·寄存器偏移<br>前索引** | [HL.LB.PR](../../inst/misa_h/HL.LB.PR.md), [HL.LH.PR](../../inst/misa_h/HL.LH.PR.md), [HL.LW.PR](../../inst/misa_h/HL.LW.PR.md), [HL.LD.PR](../../inst/misa_h/HL.LD.PR.md), [HL.LBU.PR](../../inst/misa_h/HL.LBU.PR.md), [HL.LHU.PR](../../inst/misa_h/HL.LHU.PR.md), [HL.LWU.PR](../../inst/misa_h/HL.LWU.PR.md) |
| **内存加载·立即数偏移<br>前索引** | [HL.LBI.PR](../../inst/misa_h/HL.LBI.PR.md), [HL.LHI.PR](../../inst/misa_h/HL.LHI.PR.md), [HL.LWI.PR](../../inst/misa_h/HL.LWI.PR.md), [HL.LDI.PR](../../inst/misa_h/HL.LDI.PR.md), [HL.LBUI.PR](../../inst/misa_h/HL.LBUI.PR.md), [HL.LHUI.PR](../../inst/misa_h/HL.LHUI.PR.md), [HL.LWUI.PR](../../inst/misa_h/HL.LWUI.PR.md)<br>[HL.LHI.UPR](../../inst/misa_h/HL.LHI.UPR.md), [HL.LWI.UPR](../../inst/misa_h/HL.LWI.UPR.md), [HL.LDI.UPR](../../inst/misa_h/HL.LDI.UPR.md), [HL.LHUI.UPR](../../inst/misa_h/HL.LHUI.UPR.md), [HL.LWUI.UPR](../../inst/misa_h/HL.LWUI.UPR.md) |
| **内存加载·寄存器偏移<br>后索引** | [HL.LB.PO](../../inst/misa_h/HL.LB.PO.md), [HL.LH.PO](../../inst/misa_h/HL.LH.PO.md), [HL.LW.PO](../../inst/misa_h/HL.LW.PO.md), [HL.LD.PO](../../inst/misa_h/HL.LD.PO.md), [HL.LBU.PO](../../inst/misa_h/HL.LBU.PO.md), [HL.LHU.PO](../../inst/misa_h/HL.LHU.PO.md), [HL.LWU.PO](../../inst/misa_h/HL.LWU.PO.md) |
| **内存加载·立即数偏移<br>后索引** | [HL.LBI.PO](../../inst/misa_h/HL.LBI.PO.md), [HL.LHI.PO](../../inst/misa_h/HL.LHI.PO.md), [HL.LWI.PO](../../inst/misa_h/HL.LWI.PO.md), [HL.LDI.PO](../../inst/misa_h/HL.LDI.PO.md), [HL.LBUI.PO](../../inst/misa_h/HL.LBUI.PO.md), [HL.LHUI.PO](../../inst/misa_h/HL.LHUI.PO.md), [HL.LWUI.PO](../../inst/misa_h/HL.LWUI.PO.md)<br>[HL.LHI.UPO](../../inst/misa_h/HL.LHI.UPO.md), [HL.LWI.UPO](../../inst/misa_h/HL.LWI.UPO.md), [HL.LDI.UPO](../../inst/misa_h/HL.LDI.UPO.md), [HL.LHUI.UPO](../../inst/misa_h/HL.LHUI.UPO.md), [HL.LWUI.UPO](../../inst/misa_h/HL.LWUI.UPO.md) |
| **内存加载·PC相对寻址** | [HL.LB.PCR](../../inst/misa_h/HL.LB.PCR.md), [HL.LH.PCR](../../inst/misa_h/HL.LH.PCR.md), [HL.LW.PCR](../../inst/misa_h/HL.LW.PCR.md), [HL.LD.PCR](../../inst/misa_h/HL.LD.PCR.md), [HL.LBU.PCR](../../inst/misa_h/HL.LBU.PCR.md), [HL.LHU.PCR](../../inst/misa_h/HL.LHU.PCR.md), [HL.LWU.PCR](../../inst/misa_h/HL.LWU.PCR.md) |
| **内存存储·立即数偏移** | [HL.SBI](../../inst/misa_h/HL.SBI.md), [HL.SHI](../../inst/misa_h/HL.SHI.md), [HL.SWI](../../inst/misa_h/HL.SWI.md), [HL.SDI](../../inst/misa_h/HL.SDI.md), [HL.SHI.U](../../inst/misa_h/HL.SHI.U.md), [HL.SWI.U](../../inst/misa_h/HL.SWI.U.md), [HL.SDI.U](../../inst/misa_h/HL.SDI.U.md) |
| **内存对存储·寄存器偏移** | [HL.SBP](../../inst/misa_h/HL.SBP.md), [HL.SHP](../../inst/misa_h/HL.SHP.md), [HL.SWP](../../inst/misa_h/HL.SWP.md), [HL.SDP](../../inst/misa_h/HL.SDP.md), [HL.SHP.U](../../inst/misa_h/HL.SHP.U.md), [HL.SWP.U](../../inst/misa_h/HL.SWP.U.md), [HL.SDP.U](../../inst/misa_h/HL.SDP.U.md) |
| **内存对存储·立即数偏移** | [HL.SBIP](../../inst/misa_h/HL.SBIP.md), [HL.SHIP](../../inst/misa_h/HL.SHIP.md), [HL.SWIP](../../inst/misa_h/HL.SWIP.md), [HL.SDIP](../../inst/misa_h/HL.SDIP.md), [HL.SHIP.U](../../inst/misa_h/HL.SHIP.U.md), [HL.SWIP.U](../../inst/misa_h/HL.SWIP.U.md), [HL.SDIP.U](../../inst/misa_h/HL.SDIP.U.md) |
| **内存存储·寄存器偏移<br>前索引** | [HL.SB.PR](../../inst/misa_h/HL.SB.PR.md), [HL.SH.PR](../../inst/misa_h/HL.SH.PR.md), [HL.SW.PR](../../inst/misa_h/HL.SW.PR.md), [HL.SD.PR](../../inst/misa_h/HL.SD.PR.md), [HL.SH.UPR](../../inst/misa_h/HL.SH.UPR.md), [HL.SW.UPR](../../inst/misa_h/HL.SW.UPR.md), [HL.SD.UPR](../../inst/misa_h/HL.SD.UPR.md) |
| **内存存储·立即数偏移<br>前索引** | [HL.SBI.PR](../../inst/misa_h/HL.SBI.PR.md), [HL.SHI.PR](../../inst/misa_h/HL.SHI.PR.md), [HL.SWI.PR](../../inst/misa_h/HL.SWI.PR.md), [HL.SDI.PR](../../inst/misa_h/HL.SDI.PR.md), [HL.SHI.UPR](../../inst/misa_h/HL.SHI.UPR.md), [HL.SWI.UPR](../../inst/misa_h/HL.SWI.UPR.md), [HL.SDI.UPR](../../inst/misa_h/HL.SDI.UPR.md) |
| **内存存储·寄存器偏移<br>后索引** | [HL.SB.PO](../../inst/misa_h/HL.SB.PO.md), [HL.SH.PO](../../inst/misa_h/HL.SH.PO.md), [HL.SW.PO](../../inst/misa_h/HL.SW.PO.md), [HL.SD.PO](../../inst/misa_h/HL.SD.PO.md), [HL.SH.UPO](../../inst/misa_h/HL.SH.UPO.md), [HL.SW.UPO](../../inst/misa_h/HL.SW.UPO.md), [HL.SD.UPO](../../inst/misa_h/HL.SD.UPO.md) |
| **内存存储·立即数偏移<br>后索引** | [HL.SBI.PO](../../inst/misa_h/HL.SBI.PO.md), [HL.SHI.PO](../../inst/misa_h/HL.SHI.PO.md), [HL.SWI.PO](../../inst/misa_h/HL.SWI.PO.md), [HL.SDI.PO](../../inst/misa_h/HL.SDI.PO.md), [HL.SHI.UPO](../../inst/misa_h/HL.SHI.UPO.md), [HL.SWI.UPO](../../inst/misa_h/HL.SWI.UPO.md), [HL.SDI.UPO](../../inst/misa_h/HL.SDI.UPO.md) |
| **内存存储·PC相对寻址** | [HL.SB.PCR](../../inst/misa_h/HL.SB.PCR.md), [HL.SH.PCR](../../inst/misa_h/HL.SH.PCR.md), [HL.SW.PCR](../../inst/misa_h/HL.SW.PCR.md), [HL.SD.PCR](../../inst/misa_h/HL.SD.PCR.md) |
| **系统寄存器访问** | [HL.SSRGET](../../inst/misa_h/HL.SSRGET.md), [HL.SSRSET](../../inst/misa_h/HL.SSRSET.md) |

包含的64bit指令如下：

| 分类 | 指令列表 |
|-----|----------|
| **长立即数加载** | [L.ADDLI](../../inst/misa_l/L.ADDLI.md) |
| **内存加载·PC相对寻址** | [L.LB.PCR](../../inst/misa_l/L.LB.PCR.md), [L.LH.PCR](../../inst/misa_l/L.LH.PCR.md), [L.LW.PCR](../../inst/misa_l/L.LW.PCR.md), [L.LD.PCR](../../inst/misa_l/L.LD.PCR.md), [L.LBU.PCR](../../inst/misa_l/L.LBU.PCR.md), [L.LHU.PCR](../../inst/misa_l/L.LHU.PCR.md), [L.LWU.PCR](../../inst/misa_l/L.LWU.PCR.md) |
| **内存存储·PC相对寻址** | [L.SB.PCR](../../inst/misa_l/L.SB.PCR.md), [L.SH.PCR](../../inst/misa_l/L.SH.PCR.md), [L.SW.PCR](../../inst/misa_l/L.SW.PCR.md), [L.SD.PCR](../../inst/misa_l/L.SD.PCR.md) |

## 特有指令

整型标量块内特有的48bit指令如下：

| 分类 | 指令列表 |
|-----|------------|
| **立即数乘加减** | [HL.MIADD](../../inst/misa_h/HL.MIADD.md), [HL.MISUB](../../inst/misa_h/HL.MISUB.md) |
| **比特位操作** | [HL.BFI](../../inst/misa_h/HL.BFI.md), [HL.CCAT](../../inst/misa_h/HL.CCAT.md), [HL.CCATW](../../inst/misa_h/HL.CCATW.md) |
| **内存预取** | [HL.PRF](../../inst/misa_h/HL.PRF.md), [HL.PRF.A](../../inst/misa_h/HL.PRF.A.md), [HL.RRFI.U](../../inst/misa_h/HL.PRFI.U.md), [HL.PRFI.UA](../../inst/misa_h/HL.PRFI.UA.md) |


## 备注

量内暂时不支持超长指令。
