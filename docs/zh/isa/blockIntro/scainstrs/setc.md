# 跳转参数设置指令

跳转参数设置指令用于判断块间跳转的方向，在块提交时计算下个块的跳转方向。仅适用于`条件跳转`和`间接跳转`等类型的块指令。

两寄存器输入指令，可以有选择的先对右源寄存器截取低位有或无符号扩展，逻辑比较类（setc.and和setc.or）指令可以对右源寄存器取反，然后再进行比较。

|    微指令    | 汇编格式             |     描述                            |
|--------------|---------------------|-------------------------------------|
|  SETC.EQ  | setc.eq SrcL, SrcR<{.sw, .uw}> | 根据两操作数是否相等计算下个块头地址 |
|  SETC.NE  | setc.ne SrcL, SrcR<{.sw, .uw}> | 根据两操作数是否不等计算下个块头地址 |
|  SETC.AND  | setc.and SrcL, SrcR<{.sw, .uw, .not}> | 根据两操作数逻辑与结果计算下个块头地址 |
|  SETC.OR  | setc.or SrcL, SrcR<{.sw, .uw, .not}> | 根据两操作数逻辑或结果计算下个块头地址 |
|  SETC.LT  | setc.lt SrcL, SrcR<{.sw, .uw}> | 根据左操作数是否小于右操作数计算下个块头地址（有符号比较） |
|  SETC.GE   | setc.ge SrcL, SrcR<{.sw, .uw}>  | 根据左操作数是否大于等于右操作数计算下个块头地址（有符号比较） |
|  SETC.LTU  | setc.ltu SrcL, SrcR<{.sw, .uw}> | 根据左操作数是否小于右操作数计算下个块头地址（无符号比较） |
|  SETC.GEU  | setc.geu SrcL, SrcR<{.sw, .uw}> | 根据左操作数是否大于等于右操作数计算下个块头地址（无符号比较） |

编码格式如下：

![Setcommit](../../../figs/bitfield/svg/Introduction_32bit/Setcommit.svg)

|    微指令    | 汇编格式             |     描述                            |
|--------------|---------------------|-------------------------------------|
|  SETC.EQI  | setc.eqi SrcL, simm  | 根据左操作数是否等于有符号立即数计算下个块头地址  |
|  SETC.NEI  | setc.nei SrcL, simm  | 根据左操作数是否不等于有符号立即数计算下个块头地址  |
|  SETC.ANDI  | setc.andi SrcL, simm  | 根据左操作数与有符号立即数逻辑与结果计算下个块头地址  |
|  SETC.ORI  | setc.ori SrcL, simm  | 根据左操作数与有符号立即数逻辑或结果计算下个块头地址  |
|  SETC.LTI  | setc.lti SrcL, simm  | 根据左操作数是否小于有符号立即数计算下个块头地址 |
|  SETC.GEI   | setc.gei SrcL, simm  | 根据左操作数是否大于等于有符号立即数计算下个块头地址  |
|  SETC.LTUI  | setc.ltui SrcL, uimm | 根据左操作数是否小于无符号立即数计算下个块头地址  |
|  SETC.GEUI  | setc.geui SrcL, uimm | 根据左操作数是否大于等于无符号立即数计算下个块头地址  |

编码格式如下：

![Setwithimmediatecommit](../../../figs/bitfield/svg/Introduction_32bit/Setwithimmediatecommit.svg)
