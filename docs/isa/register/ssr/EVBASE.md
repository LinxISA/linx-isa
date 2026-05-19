# EVBASE

The exceptionvector base address register (Exception vector base register) is a **readable and writable (RW)** manager ACR-specific system register, indicating the base address of the exceptionvector table and responsible for jumping to the corresponding exception processing routine.

![EVBASE](../../../figs/bitfield/svg/Sysregs/EVBASE.svg)

- **BASE**: The business handler address used to save ACRn.

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | EVBASE_ACR0 | 0x0f01 |
| ACR1 | EVBASE_ACR1 | 0x1f01 |
| ACR2 | EVBASE_ACR2 | 0x2f01 |
| ... | ... | ... |
| ACRn | EVBASE_ACRn | 0xnf01 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.