# Compression directive expansion

In order to achieve good code compression effects on a series of programs, we carefully selected a series of relatively popular instructions based on the standard instruction set and added them to the compression expansion.

## header instruction

| Classification | Instructions |
| -- | -- |
| **Block end command** | [C.BSTOP](../header/BSTOP.md) |
| **Block start command** | [C.BSTART](../header/C.BSTART.md) |

## <span id="CompressI">Microinstructions</span>

| Classification | Instructions |
| -- | -- |
| **Register Move** | [C.MOVR](../inst/misa_c/C.MOVR.md) |
| **immediate move** | [C.MOVI](../inst/misa_c/C.MOVI.md) |
| **PC relative addressing** | [C.SETRET](../inst/misa_c/C.SETRET.md) |
| **branch parameter Settings** | [C.SETC.EQ](../inst/misa_c/C.SETC.EQ.md), [C.SETC.NE](../inst/misa_c/C.SETC.NE.md), [C.SETC.TGT](../inst/misa_c/C.SETC.TGT.md) |
| **Arithmetic operations** | [C.ADD](../inst/misa_c/C.ADD.md), [C.SUB](../inst/misa_c/C.SUB.md), [C.AND](../inst/misa_c/C.AND.md), [C.OR](../inst/misa_c/C.OR.md) |
| **With immediate data·arithmetic operation** | [C.ADDI](../inst/misa_c/C.ADDI.md) |
| **Memory Access** | [C.LWI](../inst/misa_c/C.LWI.md), [C.LDI](../inst/misa_c/C.LDI.md), [C.SWI](../inst/misa_c/C.SWI.md), [C.SDI](../inst/misa_c/C.SDI.md) |
| **Low-bit extension** | [C.SEXT.B](../inst/misa_c/C.SEXT.B.md), [C.SEXT.H](../inst/misa_c/C.SEXT.H.md), [C.SEXT.W](../inst/misa_c/C.SEXT.W.md), [C.ZEXT.B](../inst/misa_c/C.ZEXT.B.md), [C.ZEXT.H](../inst/misa_c/C.ZEXT.H.md), [C.ZEXT.W](../inst/misa_c/C.ZEXT.W.md) |
| **With immediate data·Comparison** | [C.CMP.EQI](../inst/misa_c/C.CMP.EQI.md), [C.CMP.NEI](../inst/misa_c/C.CMP.NEI.md) |
| **Shift operation** | [C.SLLI](../inst/misa_c/C.SLLI.md), [C.SRLI](../inst/misa_c/C.SRLI.md) |
| **system register access** | [C.SSRGET](../inst/misa_c/C.SSRGET.md) |
| **software breakpoint** | [C.EBREAK](../inst/misa_c/C.EBREAK.md) |