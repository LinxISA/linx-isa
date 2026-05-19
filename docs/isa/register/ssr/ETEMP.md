# ETEMP

The exception context saving temporary register (Exception Temporary Register) is **readable and writable (RW)** system register, which is used to save the current context information so that execution can be resumed after the exception processing is completed.

![ETEMP](../../../figs/bitfield/svg/Sysregs/ETEMP.svg)

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | ETEMP_ACR0 | 0x0f05 |
| ACR1 | ETEMP_ACR1 | 0x1f05 |
| ACR2 | ETEMP_ACR2 | 0x2f05 |
| ... | ... | ... |
| ACRn | ETEMP_ACRn | 0xnf05 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.