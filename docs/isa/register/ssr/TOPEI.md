# TOPEI

The TOPinterruptID register (Top Interrupt ID Register) is **read-only (RO)** system register, which is used to record the ID of the highest priority pending interrupt to ensure that the processor can prioritize the critical interrupt.

![TOPEI](../../../figs/bitfield/svg/Sysregs/TOPEI.svg)

**IntID**: This field represents the interruptID of the highest priority interrupt to be processed.

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | TOPEI_ACR0 | 0x0f09 |
| ACR1 | TOPEI_ACR1 | 0x1f09 |
| ACR2 | TOPEI_ACR2 | 0x2f09 |
| ACR3 | TOPEI_ACR3 | 0x3f09 |
| ACRn | TOPEI_ACRn | 0xnf09 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.