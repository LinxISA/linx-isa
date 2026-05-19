# IPENDING

The interrupt Pending Register (Interrupt Pending Register) is **read-only (RO)** system register and is used to display all pending interrupt visible to ACRn to determine when the processor responds to interrupt.

![IPENDING](../../../figs/bitfield/svg/Sysregs/IPENDING.svg)

Among them:

- E bit mapped to external interrupt
- T bit maps to timer interrupt
- I bit mapped to inter-core interrupt (IPI)

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | IPENDING_ACR0 | 0x0f08 |
| ACR1 | IPENDING_ACR1 | 0x1f08 |
| ACR2 | IPENDING_ACR2 | 0x2f08 |
| ... | IPENDING_ACR3 | 0x3f08 |
| ACR4 | IPENDING_ACR4 | 0x4f08 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.