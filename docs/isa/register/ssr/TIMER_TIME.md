# TIMER_TIME

The timer register (Timer Register) stores the current timer count value and is usually used for timing and event scheduling within the operating system.

![TIMER_TIME](../../../figs/bitfield/svg/Sysregs/TIMER_TIME.svg)

This register is **readable and writable (RW)** and will automatically increase over time after reset.

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | TIMER_TIME_ACR0 | 0x0f20 |
| ACR1 | TIMER_TIME_ACR1 | 0x1f20 |
| ACR2 | TIMER_TIME_ACR2 | 0x2f20 |
| ... | ... | ... |
| ACRn | TIMER_TIME_ACRn | 0xnf20 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.