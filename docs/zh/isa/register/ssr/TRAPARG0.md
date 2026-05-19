# TRAPARG0

异常参数0寄存器（Trap Argument 0 Register）是 **可读写的(RW)** 的系统寄存器，用于存储服务请求过程中的异常参数0。

![TRAPARG0](../../../figs/bitfield/svg/Sysregs/TRAPARG0.svg)

## 地址空间

该寄存器在每个ACR中的命名和地址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | TRAPARG0_ACR0  | 0x0f03 |
| ACR1   | TRAPARG0_ACR1  | 0x1f03 |
| ACR2   | TRAPARG0_ACR2  | 0x2f03 |
| ...   | ...  | ... |
| ACRn   | TRAPARG0_ACRn  | 0xnf03 |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
