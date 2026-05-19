# 乘法指令

|    微指令    |            汇编格式              |     描述                                                 |
|--------------|-----------------------------------|-------------------------------------------------------|
|  MUL    |  mul SrcL, SrcR, ->{t,u,Rd}    |  两64位有符号乘法，结果低64位写到RegDst  |
|  MULU   |  mulu SrcL, SrcR, ->{t,u,Rd}   |  两64位无符号乘法，结果低64位写到RegDst  |
|  MULW   |  mulw SrcL, SrcR, ->{t,u,Rd}   |  两32位有符号乘法，结果取低32位有符号扩展后写到RegDst  |
|  MULUW  |  muluw SrcL, SrcR, ->{t,u,Rd}  |  两32位无符号乘法，结果取低32位无符号扩展后写到RegDst  |
|  MADD   |  madd SrcL, SrcR, SrcD, ->{t,u,Rd}   |  两64位有符号乘，再加一个64位，结果写到RegDst  |
|  MADDW  |  maddw SrcL, SrcR, SrcD, ->{t,u,Rd}  |  两32位有符号乘，再加一个32位，结果取低32位符号扩展后写到RegDst  |

编码如下：

![Multi-CycleALU](../../../figs/bitfield/svg/Introduction_32bit/multiInstruction.svg)


<!-- 
|  MULH   |  mulh SrcL, SrcR, ->{t,u,Rd}   |  两64位有符号乘法，高64位写到T，低64位写到RegDst  |
|  MULHU  |  mulhu SrcL, SrcR, ->{t,u,Rd}  |  两64位无符号乘法，高64位写到T，低64位写到RegDst  |
 -->
