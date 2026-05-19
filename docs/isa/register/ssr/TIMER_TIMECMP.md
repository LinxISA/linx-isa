# TIMER_TIMECMP

The timer comparator register (Timer Compare Register) is **readable and writable (RW)** system register, which is used for the comparison operation of the timer. When the timer reaches the set value, the interrupt is triggered. The compiler can use this register to implement scheduled tasks.

![TIMER_TIMECMP](../../../figs/bitfield/svg/Sysregs/TIMER_TIMECMP.svg)

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | TIMER_TIMECMP_ACR0 | 0x0f21 |
| ACR1 | TIMER_TIMECMP_ACR1 | 0x1f21 |
| ACR2 | TIMER_TIMECMP_ACR2 | 0x2f21 |
| ... | ... | ... |
| ACRn | TIMER_TIMECMP_ACRn | 0xnf21 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.