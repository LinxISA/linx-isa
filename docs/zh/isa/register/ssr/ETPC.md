# ETPC

**异常指令指针（TPC of Exception Instruction）** 是一个64bit **可读写（RW）** 的寄存器，用于存储发生异常指令的TPC，提供给软件调试以及异常处理完成后返回到原指令位置继续执行。

寄存器的字段定义如下：

![ETPC](../../../figs/bitfield/svg/Sysregs/ETPC.svg)

## 地址空间

该寄存器在每个ACR中的命名和寻址空间定义如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | ETPC_ACR0  | 0x0f0d |
| ACR1   | ETPC_ACR1  | 0x1f0d |
| ACR2   | ETPC_ACR2  | 0x2f0d |
| ...  | ...  | ... |
| ACRn   | ETPC_ACRn  | 0xnf0d |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
