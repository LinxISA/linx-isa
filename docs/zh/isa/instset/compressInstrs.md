# 压缩指令扩展

为了能在一系列的程序上得到良好的代码压缩效果，我们基于标准指令集精心挑选了一系列热度比较高的指令添加到压缩扩展。

## 块头指令

| 分类 | 指令 |
|  -- | -- |
| **块结束指令** | [C.BSTOP](../header/BSTOP.md) |
| **块起始指令** | [C.BSTART](../header/C.BSTART.md) |

## <span id="CompressI">微指令</span>

| 分类 | 指令 |
| -- | -- |
| **寄存器移动** | [C.MOVR](../inst/misa_c/C.MOVR.md) |
| **立即数移动** | [C.MOVI](../inst/misa_c/C.MOVI.md) | 
| **PC相对寻址** | [C.SETRET](../inst/misa_c/C.SETRET.md) |
| **跳转参数设置** | [C.SETC.EQ](../inst/misa_c/C.SETC.EQ.md), [C.SETC.NE](../inst/misa_c/C.SETC.NE.md), [C.SETC.TGT](../inst/misa_c/C.SETC.TGT.md) |
| **算术运算** | [C.ADD](../inst/misa_c/C.ADD.md), [C.SUB](../inst/misa_c/C.SUB.md), [C.AND](../inst/misa_c/C.AND.md), [C.OR](../inst/misa_c/C.OR.md) |
| **带立即数·算术运算** | [C.ADDI](../inst/misa_c/C.ADDI.md) |
| **内存访问** | [C.LWI](../inst/misa_c/C.LWI.md), [C.LDI](../inst/misa_c/C.LDI.md), [C.SWI](../inst/misa_c/C.SWI.md), [C.SDI](../inst/misa_c/C.SDI.md) |
| **低位扩展** | [C.SEXT.B](../inst/misa_c/C.SEXT.B.md), [C.SEXT.H](../inst/misa_c/C.SEXT.H.md), [C.SEXT.W](../inst/misa_c/C.SEXT.W.md), [C.ZEXT.B](../inst/misa_c/C.ZEXT.B.md), [C.ZEXT.H](../inst/misa_c/C.ZEXT.H.md), [C.ZEXT.W](../inst/misa_c/C.ZEXT.W.md) |
| **带立即数·比较** | [C.CMP.EQI](../inst/misa_c/C.CMP.EQI.md), [C.CMP.NEI](../inst/misa_c/C.CMP.NEI.md) |
| **移位操作** | [C.SLLI](../inst/misa_c/C.SLLI.md), [C.SRLI](../inst/misa_c/C.SRLI.md) |
| **系统寄存器访问** | [C.SSRGET](../inst/misa_c/C.SSRGET.md) |
| **软件断点** |  [C.EBREAK](../inst/misa_c/C.EBREAK.md) |
