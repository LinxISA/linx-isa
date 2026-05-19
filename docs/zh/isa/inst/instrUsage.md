# 指令应用说明

本小节基于LinxISA-0.4版本的指令定义，列举一些用户常用的操作以及部分特殊用法所对应的指令，方便用户在写程序时快速找到合适的指令完成指定的操作。

## 适用于所有块

|   操作     |    指令                   |        特殊说明                         |
|------------|---------------------------|-------------------------------------|
|  空操作nop |  addi zero, 0, ->{t, u} |    |
|  寄存器移动   |  32bit版本: addi SrcL, 0, ->{t, u, Rd}<br>16bit版本: c.movr SrcL, ->{t, u, Rd}  |     |
|  立即数加载  |  c.movi imm, ->{t, u, Rd}       |  适用立即数范围：[-16, 15]   |
|  立即数加载  |  addi zero, imm, ->{t, u, Rd}   |  适用立即数范围: [0, 4095]   |
|  立即数加载  |  subi zero, -imm, ->{t, u, Rd}  |  适用立即数范围：[-4095, 0]   |
|  等于零比较    |  cmp.eqi SrcL, 0, ->{t, u, Rd}  |    |
|  不等于零比较  |  cmp.nei SrcL, 0, ->{t, u, Rd}  |    |
|  小于零比较    |  cmp.lti SrcL, 0, ->{t, u, Rd}  |    |
|  大于零比较    |  cmp.gei SrcL, 0, ->{t, u, Rd}  |    |
|  寄存器低8位符号位扩展    |  32bit版本: bxs SrcL, 0, 8, ->{t, u, Rd}<br>16bit版本: c.sext.b SrcL, ->t   |     |
|  寄存器低16位符号位扩展   |  32bit版本: bxs SrcL, 0, 16, ->{t, u, Rd}<br>16bit版本: c.sext.h SrcL, ->t  |     |
|  寄存器低32位符号位扩展   |  32bit版本: bxs SrcL, 0, 32, ->{t, u, Rd}<br>16bit版本: c.sext.w SrcL, ->t  |     |
|  寄存器低8位无符号扩展   |  32bit版本: bxu SrcL, 0, 8, ->{t, u, Rd}<br>16bit版本: c.zext.b SrcL, ->t  |     |
|  寄存器低16位无符号扩展  |  32bit版本: bxu SrcL, 0, 16, ->{t, u, Rd}<br>16bit版本: c.zext.h SrcL, ->t |     |
|  寄存器低32位无符号扩展  |  32bit版本: bxu SrcL, 0, 32, ->{t, u, Rd}<br>16bit版本: c.zext.w SrcL, ->t |     |
|  按位取反not          |  or zero, SrcR.not, ->{t, u, Rd}    |    |
|  字按位取反not word   |  orw zero, SrcR.not, ->{t, u, Rd}    |    |
|  取负negative          |  add zero, SrcL.neg, ->{t, u, Rd}   |    |
|  字取负negative word   |  addw zero, SrcL.neg, ->{t, u, Rd}  |    |
|  读系统寄存器  |  ssrget SSR_ID, ->{t, u, Rd}  |  用于访问SSR_ID[15:12]为0的SSR  |
|  写系统寄存器  |  ssrset SSR_ID, ->{t, u, Rd}  |  用于访问SSR_ID[15:12]为0的SSR  |
|  系统寄存器与通用寄存器交换 | ssrswap SrcL, SSR_ID, ->{t, u, Rd}  | 交换SrcL的值和SSR[ID]的值 |
|  循环左移X位  |  bxu SrcL, M, 64, ->{t, u, Rd}  | M设置为64-X   |
|  循环右移X位  |  bxu SrcL, M, 64, ->{t, u, Rd}  | M设置为X   |
|  按位置零  |  bic SrcL, M, N, ->{t, u, Rd}   | 从第M位至M+N-1位置零 |
|  按位置一  |  bis SrcL, M, N, ->{t, u, Rd}   | 从第M位至M+N-1位置一 |
|  地址生成，偏移一字节对齐  |  add SrcL, SrcR.sw, ->{t, u, Rd}     |  SrcL + sext(SrcR[31:0])  |
|  地址生成，偏移两字节对齐  |  add SrcL, SrcR.sw<<1, ->{t, u, Rd}  |  SrcL + sext(SrcR[31:0])<<1  |
|  地址生成，偏移四字节对齐  |  add SrcL, SrcR.sw<<2, ->{t, u, Rd}  |  SrcL + sext(SrcR[31:0])<<2  |
|  地址生成，偏移八字节对齐  |  add SrcL, SrcR.sw<<3, ->{t, u, Rd}  |  SrcL + sext(SrcR[31:0])<<3  |
|  地址生成，偏移一字节对齐  |  add SrcL, SrcR.uw, ->{t, u, Rd}     |  SrcL + zext(SrcR[31:0])  |
|  地址生成，偏移两字节对齐  |  add SrcL, SrcR.uw<<1, ->{t, u, Rd}  |  SrcL + zext(SrcR[31:0])<<1  |
|  地址生成，偏移四字节对齐  |  add SrcL, SrcR.uw<<2, ->{t, u, Rd}  |  SrcL + zext(SrcR[31:0])<<2  |
|  地址生成，偏移八字节对齐  |  add SrcL, SrcR.uw<<3, ->{t, u, Rd}  |  SrcL + zext(SrcR[31:0])<<3  |
|  地址生成，偏移两字节对齐  |  add SrcL, SrcR<<1, ->{t, u, Rd}  |  SrcL + SrcR<<1  |
|  地址生成，偏移四字节对齐  |  add SrcL, SrcR<<2, ->{t, u, Rd}  |  SrcL + SrcR<<2  |
|  地址生成，偏移八字节对齐  |  add SrcL, SrcR<<3, ->{t, u, Rd}  |  SrcL + SrcR<<3  |

## 适用于标量块和模版块

|   操作     |    指令                   |        特殊说明                         |
|------------|---------------------------|-------------------------------------|
|  条件选择    |  csel SrcP, SrcL, SrcR, ->{t, u, Rd}  | 根据SrcP是否等于0选择SrcL或SrcR |
|  字节序反转  |  rev16 SrcL, ->{t, u, Rd}   | 反转每个16bit半字内的2个字节的顺序 |
|  字节序反转  |  rev32 SrcL, ->{t, u, Rd}   | 反转每个32bit字内的4个字节的顺序 |
|  字节序反转  |  rev64 SrcL, ->{t, u, Rd}   | 反转64bit双字内的字节顺序 |
|  拼接移位    |  ccat SrcL, SrcR, shamt, ->{t, u, Rd}  | shamt为循环左移位数  |
|  循环左移X位  |  ccat SrcL, SrcL, X, ->{t, u, Rd}  | 两输入寄存器相同  |
|  循环右移X位  |  ccat SrcL, SrcL, 64-X, ->{t, u, Rd}  | 两输入寄存器相同  |
|  高低位字交换 |  ccat SrcL, SrcL, 32, ->{t, u, Rd}  | 两输入寄存器相同  |
|  字节截取替换 |  bfi SrcL, SrcR, M, N, ->{t, u, Rd} | 截取SrcR低位N个字节，替换SrcL的M至M+N-1字节 |
|  计数前导零  |  clz SrcL, ->{t, u, Rd}  |  用于计算64bit范围内高位连续0的位数 |
|  计数前导零  |  clzw SrcL, ->{t, u, Rd} |  用于计算低32bit范围内高位连续0的位数 | 
|  计数尾随零  |  ctz SrcL, ->{t, u, Rd}  |  用于计算64bit范围内低位连续0的位数 |
|  计数尾随零  |  ctzw SrcL, ->{t, u, Rd} |  用于计算低32bit范围内低位连续0的位数 | 

## 适用于系统块

|   操作     |    指令                   |        特殊说明                         |
|------------|---------------------------|-------------------------------------|
|  读系统寄存器  |  hl.ssrget  SSR_ID, ->{t, u, Rd}  |  可访问所有SSR  |
|  写系统寄存器  |  hl.ssrset  SSR_ID, ->{t, u, Rd}  |  可访问所有SSR  |

## 适用于浮点块

|   操作     |    指令                   |        特殊说明                         |
|------------|---------------------------|-------------------------------------|
|  条件选择    |  csel SrcP, SrcL, SrcR, ->{t, u, Rd}  | 根据SrcP是否等于0选择SrcL或SrcR |
|  字节序反转  |  rev16 SrcL, ->{t, u, Rd}   | 反转每个16bit半字内的2个字节的顺序 |
|  字节序反转  |  rev32 SrcL, ->{t, u, Rd}   | 反转每个32bit字内的4个字节的顺序   |
|  字节序反转  |  rev64 SrcL, ->{t, u, Rd}   | 反转整个64bit双字内的字节顺序      |
|  计数前导零  |  clz SrcL, ->{t, u, Rd}  |  用于计算64bit范围内高位连续0的位数   |
|  计数前导零  |  clzw SrcL, ->{t, u, Rd} |  用于计算低32bit范围内高位连续0的位数 | 
|  计数尾随零  |  ctz SrcL, ->{t, u, Rd}  |  用于计算64bit范围内低位连续0的位数   |
|  计数尾随零  |  ctzw SrcL, ->{t, u, Rd} |  用于计算低32bit范围内低位连续0的位数 |
