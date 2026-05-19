# TRAPARG0

The exception parameter 0 register (Trap Argument 0 Register) is **readable and writable (RW)** system register, used to store exception parameter 0 during the service request process.

![TRAPARG0](../../../figs/bitfield/svg/Sysregs/TRAPARG0.svg)

## Address space

The naming and address space of this register differ in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | TRAPARG0_ACR0 | 0x0f03 |
| ACR1 | TRAPARG0_ACR1 | 0x1f03 |
| ACR2 | TRAPARG0_ACR2 | 0x2f03 |
| ... | ... | ... |
| ACRn | TRAPARG0_ACRn | 0xnf03 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.