# SYSCNT

本地时间戳寄存器（System Counter Register）用于同步大核时间戳, 大核从外部更新，每个核一个。

![SYSCNT](../../../figs/bitfield/svg/Sysregs/SYSCNT.svg)

## 备注

该寄存器为轻核自定义的 **只读的(RO)** 系统寄存器，其SSRID为**0x0810**。
