# EBARG

**异常块参数（Arguments of Exception Block）** 是一个64bit **可读写（RW）**的寄存器，用于存储异常块指令的跳转方式、块类型以及输出寄存器等参数。

寄存器的字段定义如下：

![EBARG](../../../figs/bitfield/svg/Sysregs/EBARG.svg)

该寄存器的所有字段与[BARG](../common/barg.md)寄存器的定义相同。

## 地址空间

该寄存器在每个ACR中的命名和寻址空间定义如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | EBARG_ACR0  | 0x0f0c |
| ACR1   | EBARG_ACR1  | 0x1f0c |
| ACR2   | EBARG_ACR2  | 0x2f0c |
| ...  | ...  | ... |
| ACRn   | EBARG_ACRn  | 0xnf0c |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
