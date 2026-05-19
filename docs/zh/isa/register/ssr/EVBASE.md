# EVBASE

异常向量基址寄存器（Exception vector base register）是一个 **可读写的(RW)** 管理者ACR特定的系统寄存器，指示异常向量表的基址，负责跳转到对应的异常处理例程。

![EVBASE](../../../figs/bitfield/svg/Sysregs/EVBASE.svg)

- **BASE**：用于保存 ACRn 的业务处理程序地址。

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | EVBASE_ACR0  | 0x0f01 |
| ACR1   | EVBASE_ACR1  | 0x1f01 |
| ACR2   | EVBASE_ACR2  | 0x2f01 |
| ...   | ...  | ... |
| ACRn   | EVBASE_ACRn  | 0xnf01 |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
