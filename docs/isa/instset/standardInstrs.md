# 标准指令扩展

标准指令扩展中的指令长度统一为标准的32位，它们包括部分特殊块类型所引入的特定功能的指令。

## <span id="StdI">微指令</span>

系统块在标准扩展中定义的指令内容如下：

| 分类  | 指令列表  |
|-------|--------------|
| **执行控制** | [BSE](../inst/misa_s/BSE.md), [BWE](../inst/misa_s/BWE.md), [BWI](../inst/misa_s/BWI.md), [BWT](../inst/misa_s/BWT.md), [ASSERT](../inst/misa_s/ASSERT.md), [ACRC](../inst/misa_s/ACRC.md), [ACRE](../inst/misa_s/ACRE.md), [DSB](../inst/misa_s/DSB.md) |
| **屏障作用** | [DSB](../inst/misa_s/DSB.md), [ISB](../inst/misa_s/ISB.md) |
| **缓存管理** | [BC.IVA](../inst/misa_s/BC.IVA.md), [BC.IALL](../inst/misa_s/BC.IALL.md), [IC.IVA](../inst/misa_s/IC.IVA.md), [IC.IALL](../inst/misa_s/IC.IALL.md), [DC.IVA](../inst/misa_s/DC.IVA.md), [DC.IALL](../inst/misa_s/DC.IALL.md), [DC.CVA](../inst/misa_s/DC.CVA.md), [DC.CIVA](../inst/misa_s/DC.CIVA.md), [DC.ISW](../inst/misa_s/DC.ISW.md), [DC.CSW](../inst/misa_s/DC.CSW.md), [DC.CISW](../inst/misa_s/DC.CISW.md), [DC.ZVA](../inst/misa_s/DC.ZVA.md) |
| **页表维护** | [TLB.IA](../inst/misa_s/TC.IA.md), [TLB.IV](../inst/misa_s/TC.IV.md), [TLB.IAV](../inst/misa_s/TC.IAV.md), [TLB.IALL](../inst/misa_s/TC.IALL.md) |
| **加载保留与条件存储** | [LR.B](../inst/misa_s/LR.B.md), [LR.H](../inst/misa_s/LR.H.md), [LR.W](../inst/misa_s/LR.W.md), [LR.D](../inst/misa_s/LR.D.md), [SC.B](../inst/misa_s/SC.B.md), [SC.H](../inst/misa_s/SC.H.md), [SC.W](../inst/misa_s/SC.W.md), [SC.D](../inst/misa_s/SC.D.md) |
| **原子操作·加载字** | [LW.ADD](../inst/misa_s/LW.ADD.md), [LW.AND](../inst/misa_s/LW.AND.md), [LW.OR](../inst/misa_s/LW.OR.md), [LW.XOR](../inst/misa_s/LW.XOR.md), [LW.SMAX](../inst/misa_s/LW.SMAX.md), [LW.SMIN](../inst/misa_s/LW.SMIN.md), [LW.UMAX](../inst/misa_s/LW.UMAX.md), | [LW.UMIN](../inst/misa_s/LW.UMIN.md) |
| **原子操作·加载双字** | [LD.ADD](../inst/misa_s/LD.ADD.md), [LD.AND](../inst/misa_s/LD.AND.md), [LD.OR](../inst/misa_s/LD.OR.md), [LD.XOR](../inst/misa_s/LD.XOR.md), [LD.SMAX](../inst/misa_s/LD.SMAX.md), [LD.SMIN](../inst/misa_s/LD.SMIN.md), [LD.UMAX](../inst/misa_s/LD.UMAX.md), | [LD.UMIN](../inst/misa_s/LD.UMIN.md) |
| **原子操作·存储字** | [SW.ADD](../inst/misa_s/SW.ADD.md), [SW.AND](../inst/misa_s/SW.AND.md), [SW.OR](../inst/misa_s/SW.OR.md), [SW.XOR](../inst/misa_s/SW.XOR.md), [SW.SMAX](../inst/misa_s/SW.SMAX.md), [SW.SMIN](../inst/misa_s/SW.SMIN.md), [SW.UMAX](../inst/misa_s/SW.UMAX.md), | [SW.UMIN](../inst/misa_s/SW.UMIN.md) |
| **原子操作·存储双字** | [SD.ADD](../inst/misa_s/SD.ADD.md), [SD.AND](../inst/misa_s/SD.AND.md), [SD.OR](../inst/misa_s/SD.OR.md), [SD.XOR](../inst/misa_s/SD.XOR.md), [SD.SMAX](../inst/misa_s/SD.SMAX.md), [SD.SMIN](../inst/misa_s/SD.SMIN.md), [SD.UMAX](../inst/misa_s/SD.UMAX.md), | [SD.UMIN](../inst/misa_s/SD.UMIN.md) |
| **原子交换** | [SWAPB](../inst/misa_s/SWAPB.md), [SWAPH](../inst/misa_s/SWAPH.md), [SWAPW](../inst/misa_s/SWAPW.md), [SWAPD](../inst/misa_s/SWAPD.md) |
| **浮点运算** | [FADD](../inst/misa_f/FADD.md), [FSUB](../inst/misa_f/FSUB.md), [FMUL](../inst/misa_f/FMUL.md), [FDIV](../inst/misa_f/FDIV.md), [FMADD](../inst/misa_f/FMADD.md), [FMSUB](../inst/misa_f/FMSUB.md), [FNMADD](../inst/misa_f/FNMADD.md), [FNMSUB](../inst/misa_f/FNMSUB.md) |
| **浮点比较** | [FEQ](../inst/misa_f/FEQ.md), [FNE](../inst/misa_f/FNE.md), [FLT](../inst/misa_f/FLT.md), [FGE](../inst/misa_f/FGE.md), [FEQS](../inst/misa_f/FEQS.md), [FNES](../inst/misa_f/FNES.md), [FLTS](../inst/misa_f/FLTS.md), [FGES](../inst/misa_f/FGES.md) |
| **最大最小值** | [MAX](../inst/misa_f/MAX.md), [MIN](../inst/misa_f/MIN.md), [FMAX](../inst/misa_f/FMAX.md), [FMIN](../inst/misa_f/FMIN.md) |
| **数据格式转换** | [FCVT](../inst/misa_f/FCVT.md), [FCVTA](../inst/misa_f/FCVTA.md), [FCVTM](../inst/misa_f/FCVTM.md), [FCVTN](../inst/misa_f/FCVTN.md), [FCVTP](../inst/misa_f/FCVTP.md), [FCVTZ](../inst/misa_f/FCVTZ.md), [SCVTF](../inst/misa_f/SCVTF.md), [UCVTF](../inst/misa_f/UCVTF.md) |
| **浮点特殊运算** | [FABS](../inst/misa_f/FABS.md), [FSQRT](../inst/misa_f/FSQRT.md), [FRECIP](../inst/misa_f/FRECIP.md), [FEXP](../inst/misa_f/FEXP.md) |
