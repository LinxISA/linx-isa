# EBPC

**exception block pointer (BPC of Exception Block)** is a 64bit **readable and writable (RW)** The register is used to store the BPC of exceptionblock instruction, which is provided for software debugging and to continue execution from exceptionblock instruction after exception returns.

The fields of the register are defined as follows:

![EBPC](../../../figs/bitfield/svg/Sysregs/EBPC.svg)

## Address space

The naming and addressing space of this register in each ACR is defined as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | EBPC_ACR0 | 0x0f0b |
| ACR1 | EBPC_ACR1 | 0x1f0b |
| ACR2 | EBPC_ACR2 | 0x2f0b |
| ... | ... | ... |
| ACRn | EBPC_ACRn | 0xnf0b |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.