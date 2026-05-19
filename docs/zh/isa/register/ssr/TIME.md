# TIME

定时器计数寄存器（Timer Counter Register）是记录处理器的全局时间戳的系统寄存器。该寄存器可用于计时和事件驱动的调度，编译器可用来优化时间敏感任务。

![TIME](../../../figs/bitfield/svg/Sysregs/TIME.svg)

## 备注

该寄存器是 **只读的(RO)**，其SSRID为**0x0010**。
