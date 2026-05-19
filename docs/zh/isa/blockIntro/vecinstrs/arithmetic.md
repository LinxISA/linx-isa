# 整数运算指令

向量整数运算指令可实现每个执行通道（Lane）中 `64位`、`32位`、`16位`或`8位`的整型数据的算术运算和逻辑运算操作，数据位宽通过操作数的后缀 `d,w,h,b` 等进行标识。

## 指令列表

两个寄存器操作数的指令列表如下：

|  指令 | 汇编格式      |     描述                            |
|---------------|--------------|-------------------------------------|
| V.ADD | `v.add SrcL.{T}, SrcR.{T}<<<shamt>, ->Dst.{W}` | 加法 |
| V.SUB | `v.sub SrcL.{T}, SrcR.{T}<<<shamt>, ->Dst.{W}` | 减法 |
| V.AND | `v.and SrcL.{T}, SrcR.{T}<<<shamt>, ->Dst.{W}` | 逻辑与 |
| V.OR  | `v.or SrcL.{T}, SrcR.{T}<<<shamt>, ->Dst.{W}`  | 逻辑或 |
| V.XOR | `v.xor SrcL.{T}, SrcR.{T}<<<shamt>, ->Dst.{W}` | 逻辑异或 |
| V.SRL | `v.srl SrcL.{T}, SrcR.{T}, ->Dst.{W}` | 逻辑右移 |
| V.SRA | `v.sra SrcL.{T}, SrcR.{T}, ->Dst.{W}` | 算术右移 |
| V.SLL | `v.sll SrcL.{T}, SrcR.{T}, ->Dst.{W}` | 逻辑左移 |

一个寄存器操作数加一个立即数操作数的指令列表如下：

|  指令 | 汇编格式       |     描述                            |
|---------------|---------------|-------------------------------------|
| V.ADDI | `v.addi SrcL.{T}, uimm, ->Dst.{W}` | 无符号立即数加法 |
| V.SUBI | `v.subi SrcL.{T}, uimm, ->Dst.{W}` | 无符号立即数减法 |
| V.ANDI | `v.andi SrcL.{T}, simm, ->Dst.{W}` | 有符号立即数逻辑与 |
| V.ORI  | `v.ori SrcL.{T}, simm, ->Dst.{W}`  | 有符号立即数逻辑或 |
| V.XORI | `v.xori SrcL.{T}, simm, ->Dst.{W}` | 有符号立即数逻辑异或 |
| V.SRLI | `v.srli SrcL.{T}, shamt, ->Dst.{W}` | 无符号立即数逻辑右移 |
| V.SRAI | `v.srai SrcL.{T}, shamt, ->Dst.{W}` | 无符号立即数算术右移 |
| V.SLLI | `v.slli SrcL.{T}, shamt, ->Dst.{W}` | 无符号立即数逻辑左移 |

## 指令编码

![IntArthmetic](../../../figs/bitfield/svg/Introduction_64bit/ArithmeticOperationVector.svg)
