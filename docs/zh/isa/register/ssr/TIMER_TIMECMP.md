# TIMER_TIMECMP

定时器比较器寄存器（Timer Compare Register）是 **可读写的(RW)** 的系统寄存器，用于定时器的比较操作，当定时器达到设定值时触发中断。编译器可利用该寄存器实现定时任务。

![TIMER_TIMECMP](../../../figs/bitfield/svg/Sysregs/TIMER_TIMECMP.svg)

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | TIMER_TIMECMP_ACR0  | 0x0f21 |
| ACR1   | TIMER_TIMECMP_ACR1  | 0x1f21 |
| ACR2   | TIMER_TIMECMP_ACR2  | 0x2f21 |
| ...   | ...  | ... |
| ACRn   | TIMER_TIMECMP_ACRn  | 0xnf21 |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
