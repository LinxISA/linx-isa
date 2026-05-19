# XBINFO

The XB block initialization register (Cross Block Info Register) is **readable and writable (RW)** system register, used to save the entry address when system-call block (XB block) and cross-ACR calls, and supports inter-core communication and cross-core function calls.

![XBINFO](../../../figs/bitfield/svg/Sysregs/XBINFO.svg)

**BASE**: The BASE field segment saves the entry base address of the current ACR that is called across the ACR to the current ACR. It requires 32-byte alignment. The complete entry address is: BASE<<5. The table memory content pointed to by BASE does not exceed one 4KB page and cannot span the alignment boundary of two 4KB pages. Anything beyond that will be ignored.

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | XBINFO_ACR0 | 0x0f30 |
| ACR1 | XBINFO_ACR1 | 0x1f30 |
| ACR2 | XBINFO_ACR2 | 0x2f30 |
| ACR3 | XBINFO_ACR3 | 0x3f30 |
| ACR4 | XBINFO_ACR4 | 0x4f30 |
| ACR5 | XBINFO_ACR5 | 0x5f30 |
| ACR6 | XBINFO_ACR6 | 0x6f30 |
| ACR7 | XBINFO_ACR7 | 0x7f30 |
| ACR8 | XBINFO_ACR8 | 0x8f30 |
| ACR9 | XBINFO_ACR9 | 0x9f30 |
| ACR10 | XBINFO_ACR10 | 0xaf30 |
| ACR11 | XBINFO_ACR11 | 0xbf30 |
| ACR12 | XBINFO_ACR12 | 0xcf30 |
| ACR13 | XBINFO_ACR13 | 0xdf30 |
| ACR14 | XBINFO_ACR14 | 0xef30 |
| ACR15 | XBINFO_ACR15 | 0xff30 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.