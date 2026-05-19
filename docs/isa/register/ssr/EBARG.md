# EBARG

**exception block parameters (Arguments of Exception Block)** is a 64bit **readable and writable (RW)** register, used to store the jump mode of exceptionblock instruction, block type and output registers and other parameters.

The fields of the register are defined as follows:

![EBARG](../../../figs/bitfield/svg/Sysregs/EBARG.svg)

All fields of this register have the same definitions as the [BARG](../common/barg.md) register.

## Address space

The naming and addressing space of this register in each ACR is defined as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | EBARG_ACR0 | 0x0f0c |
| ACR1 | EBARG_ACR1 | 0x1f0c |
| ACR2 | EBARG_ACR2 | 0x2f0c |
| ... | ... | ... |
| ACRn | EBARG_ACRn | 0xnf0c |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.