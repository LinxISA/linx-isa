# 除法指令

|    微指令    |     汇编格式          |     描述                             |
|--------------|-----------------------|-------------------------------------|
|  DIV    |  div SrcL, SrcR, ->{t,u,Rd}    |  两个64位值有符号除法，商数写到目的寄存器  |
|  DIVU   |  divu SrcL, SrcR, ->{t,u,Rd}   |  两个64位值无符号除法，商数写到目的寄存器  |
|  DIVW   |  divw SrcL, SrcR, ->{t,u,Rd}   |  两个32位值有符号除法，商数写到目的寄存器  |
|  DIVUW  |  divuw SrcL, SrcR, ->{t,u,Rd}  |  两个32位值无符号除法，商数写到目的寄存器  |
|  REM    |  rem SrcL, SrcR, ->{t,u,Rd}    |  两个64位值有符号求余，余数写到目的寄存器  |
|  REMU   |  remu SrcL, SrcR, ->{t,u,Rd}   |  两个64位值无符号求余，余数写到目的寄存器  |
|  REMW   |  remw SrcL, SrcR, ->{t,u,Rd}   |  两个32位值有符号求余，余数写到目的寄存器  |
|  REMUW  |  remuw SrcL, SrcR, ->{t,u,Rd}  |  两个32位值无符号求余，余数写到目的寄存器  |

编码如下：

![Multi-CycleALU](../../../figs/bitfield/svg/Introduction_32bit/divisionInstruction.svg)
