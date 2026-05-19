# ETEMP

异常上下文保存临时寄存器（Exception Temporary Register）是 **可读写的(RW)** 的系统寄存器，用于保存当前的上下文信息，以便在异常处理完成后恢复执行。

![ETEMP](../../../figs/bitfield/svg/Sysregs/ETEMP.svg)

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | ETEMP_ACR0  | 0x0f05 |
| ACR1   | ETEMP_ACR1  | 0x1f05 |
| ACR2   | ETEMP_ACR2  | 0x2f05 |
| ...   | ...  | ... |
| ACRn   | ETEMP_ACRn  | 0xnf05 |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
