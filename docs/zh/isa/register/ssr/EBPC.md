# EBPC

**异常块指针（BPC of Exception Block）** 是一个64bit **可读写（RW）** 的寄存器，用于存储异常块指令的BPC，提供给软件调试以及异常返回后从异常块指令继续执行。

寄存器的字段定义如下：

![EBPC](../../../figs/bitfield/svg/Sysregs/EBPC.svg)

## 地址空间

该寄存器在每个ACR中的命名和寻址空间定义如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | EBPC_ACR0  | 0x0f0b |
| ACR1   | EBPC_ACR1  | 0x1f0b |
| ACR2   | EBPC_ACR2  | 0x2f0b |
| ...  | ...  | ... |
| ACRn   | EBPC_ACRn  | 0xnf0b |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
