# TIMER_TIME

定时器寄存器（Timer Register）存储当前定时器的计数值，通常用于操作系统内的计时和事件调度。

![TIMER_TIME](../../../figs/bitfield/svg/Sysregs/TIMER_TIME.svg)

该寄存器是**可读写的(RW)**，且重置后随时间自动增加。

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | TIMER_TIME_ACR0  | 0x0f20 |
| ACR1   | TIMER_TIME_ACR1  | 0x1f20 |
| ACR2   | TIMER_TIME_ACR2  | 0x2f20 |
| ...   | ...  | ... |
| ACRn   | TIMER_TIME_ACRn  | 0xnf20 |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
