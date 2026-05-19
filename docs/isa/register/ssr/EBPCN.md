# EBPCN

**exception block target block pointer (Next BPC of Exception Block)** is a 64-bit **readable and writable (RW)** register, used to store the BPC of the next block instruction or the local return address of the exception separate block in the execution sense of exceptionblock instruction.

The fields of the register are defined as follows:

![EBPCN](../../../figs/bitfield/svg/Sysregs/EBPCN.svg)

## Address space

The naming and addressing space of this register in each ACR is defined as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | EBPCN_ACR0 | 0x0f0e |
| ACR1 | EBPCN_ACR1 | 0x1f0e |
| ACR2 | EBPCN_ACR2 | 0x2f0e |
| ... | ... | ... |
| ACRn | EBPCN_ACRn | 0xnf0e |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.