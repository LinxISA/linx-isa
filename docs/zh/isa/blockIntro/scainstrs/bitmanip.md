# 位操作指令

比特位操作类指令包括用于比特位截取或置位的 F 类型指令。

|     微指令    | 汇编格式       |     描述                            |
|---------------|---------------|-------------------------------------|
|  BXU  |  bxu  SrcL, M, N, ->{t,u,Rd}  |  从源操作数第`M`位开始连续截取`N`位并无符号扩展  |
|  BXS  |  bxs  SrcL, M, N, ->{t,u,Rd}  |  从源操作数第`M`位开始连续截取`N`位并有符号扩展  |
|  BIC  |  bic  SrcL, M, N, ->{t,u,Rd}  |  将源操作数第`M`位开始连续`N`位置位为0  |
|  BIS  |  bis  SrcL, M, N, ->{t,u,Rd}  |  将源操作数第`M`位开始连续`N`位置位为1  |
|  CTZ  | ctz SrcL, M, N, ->{t,u,Rd}    |  计数源操作数第`M`位开始连续`N`位第一个1后的0的个数  |
|  CLZ  | clz SrcL, M, N, ->{t,u,Rd}    |  计数源操作数第`M`位开始连续`N`位第一个1前的0的个数  |
|  BCNT |  bcnt SrcL, M, N, ->{t,u,Rd}  |  计数源操作数第`M`位开始连续`N`位比特位为1的位数  |
|  REV  |  rev  SrcL, M, N, ->{t,u,Rd}  |  在源操作数的`M`位的范围内以`N`位为单位进行翻转  |

编码格式如下：

![BitOperation](../../../figs/bitfield/svg/Introduction_32bit/BitOperation.svg)
