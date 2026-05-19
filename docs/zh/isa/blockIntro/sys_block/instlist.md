# 块体指令

当前版本，系统块块体中提供的指令列表如下：

## 公共指令

系统块内支持所有的公共指令，具体请见[公共指令列表](../std_block/instlist.md#puclicinsts)。

## 特有指令

系统块内独有的32bit指令如下：

| 分类  | 指令列表  |
|-------|--------------|
| **执行控制** | [BSE](../../inst/misa_s/BSE.md), [BWE](../../inst/misa_s/BWE.md), [BWI](../../inst/misa_s/BWI.md), [BWT](../../inst/misa_s/BWI.md), [ASSERT](../../inst/misa_s/ASSERT.md), [ACRC](../../inst/misa_s/ACRC.md), [ACRE](../../inst/misa_s/ACRE.md), [DSB](../../inst/misa_s/DSB.md) |
| **屏障作用** | [DSB](../../inst/misa_s/DSB.md), [ISB](../../inst/misa_s/ISB.md) |
| **缓存管理** | [BC.IVA](../../inst/misa_s/BC.IVA.md), [BC.IALL](../../inst/misa_s/BC.IALL.md), [IC.IVA](../../inst/misa_s/IC.IVA.md), [IC.IALL](../../inst/misa_s/IC.IALL.md), [DC.IVA](../../inst/misa_s/DC.IVA.md), [DC.IALL](../../inst/misa_s/DC.IALL.md), [DC.CVA](../../inst/misa_s/DC.CVA.md), [DC.CIVA](../../inst/misa_s/DC.CIVA.md), [DC.ISW](../../inst/misa_s/DC.ISW.md), [DC.CSW](../../inst/misa_s/DC.CSW.md), [DC.CISW](../../inst/misa_s/DC.CISW.md), [DC.ZVA](../../inst/misa_s/DC.ZVA.md) |
| **页表维护** | [TLB.IA](../../inst/misa_s/TC.IA.md), [TLB.IV](../../inst/misa_s/TC.IV.md), [TLB.IAV](../../inst/misa_s/TC.IAV.md), [TLB.IALL](../../inst/misa_s/TC.IALL.md) |
| **加载保留与条件存储** | [LR.B](../../inst/misa_s/LR.B.md), [LR.H](../../inst/misa_s/LR.H.md), [LR.W](../../inst/misa_s/LR.W.md), [LR.D](../../inst/misa_s/LR.D.md), [SC.B](../../inst/misa_s/SC.B.md), [SC.H](../../inst/misa_s/SC.H.md), [SC.W](../../inst/misa_s/SC.W.md), [SC.D](../../inst/misa_s/SC.D.md) |
| **原子操作·加载字** | [LW.ADD](../../inst/misa_s/LW.ADD.md), [LW.AND](../../inst/misa_s/LW.AND.md), [LW.OR](../../inst/misa_s/LW.OR.md), [LW.XOR](../../inst/misa_s/LW.XOR.md), [LW.SMAX](../../inst/misa_s/LW.SMAX.md), [LW.SMIN](../../inst/misa_s/LW.SMIN.md), [LW.UMAX](../../inst/misa_s/LW.UMAX.md), | [LW.UMIN](../../inst/misa_s/LW.UMIN.md) |
| **原子操作·加载双字** | [LD.ADD](../../inst/misa_s/LD.ADD.md), [LD.AND](../../inst/misa_s/LD.AND.md), [LD.OR](../../inst/misa_s/LD.OR.md), [LD.XOR](../../inst/misa_s/LD.XOR.md), [LD.SMAX](../../inst/misa_s/LD.SMAX.md), [LD.SMIN](../../inst/misa_s/LD.SMIN.md), [LD.UMAX](../../inst/misa_s/LD.UMAX.md), | [LD.UMIN](../../inst/misa_s/LD.UMIN.md) |
| **原子操作·存储字** | [SW.ADD](../../inst/misa_s/SW.ADD.md), [SW.AND](../../inst/misa_s/SW.AND.md), [SW.OR](../../inst/misa_s/SW.OR.md), [SW.XOR](../../inst/misa_s/SW.XOR.md), [SW.SMAX](../../inst/misa_s/SW.SMAX.md), [SW.SMIN](../../inst/misa_s/SW.SMIN.md), [SW.UMAX](../../inst/misa_s/SW.UMAX.md), | [SW.UMIN](../../inst/misa_s/SW.UMIN.md) |
| **原子操作·存储双字** | [SD.ADD](../../inst/misa_s/SD.ADD.md), [SD.AND](../../inst/misa_s/SD.AND.md), [SD.OR](../../inst/misa_s/SD.OR.md), [SD.XOR](../../inst/misa_s/SD.XOR.md), [SD.SMAX](../../inst/misa_s/SD.SMAX.md), [SD.SMIN](../../inst/misa_s/SD.SMIN.md), [SD.UMAX](../../inst/misa_s/SD.UMAX.md), | [SD.UMIN](../../inst/misa_s/SD.UMIN.md) |
| **原子交换** | [SWAPB](../../inst/misa_s/SWAPB.md), [SWAPH](../../inst/misa_s/SWAPH.md), [SWAPW](../../inst/misa_s/SWAPW.md), [SWAPD](../../inst/misa_s/SWAPD.md) |

系统块内独有的48bit指令如下：

| 分类 | 指令列表 |
|-----|----------|
| **通用队列管理** | [HL.QMT](../../inst/misa_h/HL.QMT.md), [HL.QPUSH](../../inst/misa_h/HL.QPUSH.md), [HL.QPOP](../../inst/misa_h/HL.QPOP.md) |
| **原子操作** | [HL.CASB](../../inst/misa_h/HL.CASB.md), [HL.CASH](../../inst/misa_h/HL.CASH.md), [HL.CASW](../../inst/misa_h/HL.CASW.md), [HL.CASD](../../inst/misa_h/HL.CASD.md) |

系统块内独有的64bit指令如下：

| 分类 | 指令列表 |
|-----|---------|
| **原子双元素比较交换** | [L.CASBP](../../inst/misa_l/L.CASBP.md), [L.CASHP](../../inst/misa_l/L.CASHP.md), [L.CASWP](../../inst/misa_l/L.CASWP.md), [L.CASDP](../../inst/misa_l/L.CASDP.md) |

## 指令特性

系统块内块体指令的特性包括：

- 系统块内块体指令是完备的，包括所有的基础指令。
- 系统块指令内块体指令可以被中断和产生异常。
- 系统块指令内块体指令设置系统寄存器时立即生效，无影子系统寄存器。访问系统寄存器效果和访存相同。允许在一个块指令内先设置再读取。
- 系统块指令内中断控制，系统调用，异常返回等修改BPC的指令，需要在系统块指令整体提交后生效。

## 备注

系统块内暂时不支持超长指令。
