# EBSTATEP

The exception block state pointer register (Exception Block State Pointer Register) is **readable and writable (RW)** system register, used to store the address of the exception block state when block instruction is executed, and helps the scheduler manage block recovery and restart in the exception situation.

EBSTATE can be thought of as an array of 64-bit values ​​whose contents are relevant to the block engine.

![EBSTATEP](../../../figs/bitfield/svg/Sysregs/EBSTATEP.svg)

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | EBSTATEP_ACR0 | 0x0f40 |
| ACR1 | EBSTATEP_ACR1 | 0x1f40 |
| ACR2 | EBSTATEP_ACR2 | 0x2f40 |
| ... | ... | ... |
| ACRn | EBSTATEP_ACRn | 0xnf40 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.