# 系统寄存器读写指令

该类指令用于进行系统寄存器的读写操作，实现块内状态与系统状态的交互。

这几条系统寄存器访问指令只支持访问SSR_ID[15:12]等于0的系统寄存器，否则需要使用系统块内的l.ssrget/l.ssrset指令。

|     微指令    | 汇编格式       |     描述                            |
|---------------|---------------|-------------------------------------|
|  SSRGET    |  ssrget SSR_ID, ->{t, u, Rd} |  读取SSR_ID对应的系统寄存器值至目的寄存器中  |
|  SSRSET    |  ssrset SrcL, SSR_ID         | 将源寄存器中值写到SSR_ID对应的系统寄存器中 |
|  SSRSWAP   |  ssrswap SrcL, SSR_ID, ->Rd | 原子执行将SSR_ID指定的系统寄存器的值写入目的寄存器，并将输入寄存器的值写回该系统寄存器 |
|  LSRGET    |  lsrget LSR_ID, ->{t, u, Rd} |  读取LSR_ID指定的块内状态寄存器或其某个字段的值到目的寄存器中  |
|  SETC.TGT  |  setc.tgt SrcL         |  将源寄存器中值写到LSR_ID对应的块内状态寄存器中  |

![SSRAccess](../../../figs/bitfield/svg/Introduction_32bit/ComSSRAccess.svg)
