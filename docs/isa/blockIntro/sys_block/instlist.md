# body command

In the current version, the list of instructions provided in the system block body is as follows:

## Public instructions

All public instructions are supported in the system block. For details, please see [Public Instruction List] (../std_block/instlist.md#puclicinsts).

## Special instructions

The unique 32bit instructions within the system block are as follows:| Category | Instruction List |
|-------|-------------|
| **Execution Control** | [BSE](../../inst/misa_s/BSE.md), [BWE](../../inst/misa_s/BWE.md), [BWI](../../inst/misa_s/BWI.md), [BWT](../../inst/misa_s/BWI.md), [ASSERT](../../inst/misa_s/ASSERT.md), [ACRC](../../inst/misa_s/ACRC.md), [ACRE](../../inst/misa_s/ACRE.md), [DSB](../../inst/misa_s/DSB.md) |
| **Barrier effect** | [DSB](../../inst/misa_s/DSB.md), [ISB](../../inst/misa_s/ISB.md) |
| **Cache Management** | [BC.IVA](../../inst/misa_s/BC.IVA.md), [BC.IALL](../../inst/misa_s/BC.IALL.md), [IC.IVA](../../inst/misa_s/IC.IVA.md), [IC.IALL](../../inst/misa_s/IC.IALL.md), [DC.IVA](../../inst/misa_s/DC.IVA.md), [DC.IALL](../../inst/misa_s/DC.IALL.md), [DC.CVA](../../inst/misa_s/DC.CVA.md), [DC.CIVA](../../inst/misa_s/DC.CIVA.md), [DC.ISW](../../inst/misa_s/DC.ISW.md), [DC.CSW](../../inst/misa_s/DC.CSW.md), [DC.CISW](../../inst/misa_s/DC.CISW.md), [DC.ZVA](../../inst/misa_s/DC.ZVA.md) |
| **Page table maintenance** | [TLB.IA](../../inst/misa_s/TC.IA.md), [TLB.IV](../../inst/misa_s/TC.IV.md), [TLB.IAV](../../inst/misa_s/TC.IAV.md), [TLB.IALL](../../inst/misa_s/TC.IALL.md) |
| **Load retention and conditional storage** | [LR.B](../../inst/misa_s/LR.B.md), [LR.H](../../inst/misa_s/LR.H.md), [LR.W](../../inst/misa_s/LR.W.md), [LR.D](../../inst/misa_s/LR.D.md), [SC.B](../../inst/misa_s/SC.B.md), [SC.H](../../inst/misa_s/SC.H.md), [SC.W](../../inst/misa_s/SC.W.md), [SC.D](../../inst/misa_s/SC.D.md) |
| **Atomic operation·Load word** | [LW.ADD](../../inst/misa_s/LW.ADD.md), [LW.AND](../../inst/misa_s/LW.AND.md), [LW.OR](../../inst/misa_s/LW.OR.md), [LW.XOR](../../inst/misa_s/LW.XOR.md), [LW.SMAX](../../inst/misa_s/LW.SMAX.md), [LW.SMIN](../../inst/misa_s/LW.SMIN.md), [LW.UMAX](../../inst/misa_s/LW.UMAX.md), | [LW.UMIN](../../inst/misa_s/LW.UMIN.md) |
| **Atomic operation·Load double word** | [LD.ADD](../../inst/misa_s/LD.ADD.md), [LD.AND](../../inst/misa_s/LD.AND.md), [LD.OR](../../inst/misa_s/LD.OR.md), [LD.XOR](../../inst/misa_s/LD.XOR.md), [LD.SMAX](../../inst/misa_s/LD.SMAX.md), [LD.SMIN](../../inst/misa_s/LD.SMIN.md), [LD.UMAX](../../inst/misa_s/LD.UMAX.md), | [LD.UMIN](../../inst/misa_s/LD.UMIN.md) |
| **Atomic operation·Storage word** | [SW.ADD](../../inst/misa_s/SW.ADD.md), [SW.AND](../../inst/misa_s/SW.AND.md), [SW.OR](../../inst/misa_s/SW.OR.md), [SW.XOR](../../inst/misa_s/SW.XOR.md), [SW.SMAX](../../inst/misa_s/SW.SMAX.md), [SW.SMIN](../../inst/misa_s/SW.SMIN.md), [SW.UMAX](../../inst/misa_s/SW.UMAX.md), | [SW.UMIN](../../inst/misa_s/SW.UMIN.md) || **Atomic operation·Storage double word** | [SD.ADD](../../inst/misa_s/SD.ADD.md), [SD.AND](../../inst/misa_s/SD.AND.md), [SD.OR](../../inst/misa_s/SD.OR.md), [SD.XOR](../../inst/misa_s/SD.XOR.md), [SD.SMAX](../../inst/misa_s/SD.SMAX.md), [SD.SMIN](../../inst/misa_s/SD.SMIN.md), [SD.UMAX](../../inst/misa_s/SD.UMAX.md), | [SD.UMIN](../../inst/misa_s/SD.UMIN.md) |
| **Atomic Swap** | [SWAPB](../../inst/misa_s/SWAPB.md), [SWAPH](../../inst/misa_s/SWAPH.md), [SWAPW](../../inst/misa_s/SWAPW.md), [SWAPD](../../inst/misa_s/SWAPD.md) |

The unique 48bit instructions within the system block are as follows:

| Category | Instruction List |
|-----|----------|
| **Universal Queue Management** | [HL.QMT](../../inst/misa_h/HL.QMT.md), [HL.QPUSH](../../inst/misa_h/HL.QPUSH.md), [HL.QPOP](../../inst/misa_h/HL.QPOP.md) |
| **Atomic operations** | [HL.CASB](../../inst/misa_h/HL.CASB.md), [HL.CASH](../../inst/misa_h/HL.CASH.md), [HL.CASW](../../inst/misa_h/HL.CASW.md), [HL.CASD](../../inst/misa_h/HL.CASD.md) |

The unique 64bit instructions within the system block are as follows:

| Category | Instruction List |
|-----|---------|
| **Atomic double element comparison and exchange** | [L.CASBP](../../inst/misa_l/L.CASBP.md), [L.CASHP](../../inst/misa_l/L.CASHP.md), [L.CASWP](../../inst/misa_l/L.CASWP.md), [L.CASDP](../../inst/misa_l/L.CASDP.md) |

## Command characteristics

Features of the body instruction within the system block include:

- The body instruction in the system block is complete, including all basic instructions.
- The body instruction in system block instruction can be interrupt and produce exception.
- The body command in the system block instruction takes effect immediately when setting system register, and there is no shadow system register. The effect of accessing system register is the same as accessing memory. Allows setting and then reading within a block instruction.
- interrupt control, system call, exception return and other instructions to modify the BPC in the system block instruction need to take effect after the system block instruction is submitted as a whole.

## Remarks

Very long instructions are not currently supported in the system block.