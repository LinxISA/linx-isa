# EBSTATEP

异常块状态指针寄存器（Exception Block State Pointer Register）是 **可读写的(RW)** 的系统寄存器，用于存储块指令执行时的异常块状态的地址，帮助调度器管理异常情况时的块恢复和重启。

EBSTATE可以被看做是一个64位值的数组，其内容和块引擎相关。

![EBSTATEP](../../../figs/bitfield/svg/Sysregs/EBSTATEP.svg)

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | EBSTATEP_ACR0  | 0x0f40 |
| ACR1   | EBSTATEP_ACR1  | 0x1f40 |
| ACR2   | EBSTATEP_ACR2  | 0x2f40 |
| ...   | ...  | ... |
| ACRn   | EBSTATEP_ACRn  | 0xnf40 |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
