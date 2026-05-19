# EBPCN

**异常块目标块指针（Next BPC of Exception Block）** 是一个64bit **可读写（RW）** 的寄存器，用于存储异常块指令的执行意义上下个块指令的BPC 或者 异常分离块的本地返回地址。

寄存器的字段定义如下：

![EBPCN](../../../figs/bitfield/svg/Sysregs/EBPCN.svg)

## 地址空间

该寄存器在每个ACR中的命名和寻址空间定义如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | EBPCN_ACR0  | 0x0f0e |
| ACR1   | EBPCN_ACR1  | 0x1f0e |
| ACR2   | EBPCN_ACR2  | 0x2f0e |
| ...  | ...  | ... |
| ACRn   | EBPCN_ACRn  | 0xnf0e |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
