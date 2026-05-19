# TOPEI

TOP中断ID寄存器（Top Interrupt ID Register）是 **只读的(RO)** 系统寄存器，用于记录最高优先级的挂起中断的ID，确保处理器能够优先处理关键中断。

![TOPEI](../../../figs/bitfield/svg/Sysregs/TOPEI.svg)

**IntID** ：该字段表示要处理的最高优先级中断的中断ID。

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | TOPEI_ACR0  | 0x0f09  |
| ACR1   | TOPEI_ACR1  | 0x1f09  |
| ACR2   | TOPEI_ACR2  | 0x2f09  |
| ACR3   | TOPEI_ACR3  | 0x3f09  |
| ACRn   | TOPEI_ACRn  | 0xnf09  |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
