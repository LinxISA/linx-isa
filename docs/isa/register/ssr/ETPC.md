# ETPC

**exception instruction pointer (TPC of Exception Instruction)** is a 64-bit **readable and writable (RW)** register, which is used to store the TPC where the exception instruction occurs. It is provided for software debugging and after the exception processing is completed, it returns to the original instruction location to continue execution.

The fields of the register are defined as follows:

![ETPC](../../../figs/bitfield/svg/Sysregs/ETPC.svg)

## Address space

The naming and addressing space of this register in each ACR is defined as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | ETPC_ACR0 | 0x0f0d |
| ACR1 | ETPC_ACR1 | 0x1f0d |
| ACR2 | ETPC_ACR2 | 0x2f0d |
| ... | ... | ... |
| ACRn | ETPC_ACRn | 0xnf0d |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.