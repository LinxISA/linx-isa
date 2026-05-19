# XBINFO

XB块初始化寄存器（Cross Block Info Register）是 **可读写的(RW)** 系统寄存器，用于系统调用块（XB块）和跨ACR调用时保存入口地址，支持核间通讯和跨核函数调用。

![XBINFO](../../../figs/bitfield/svg/Sysregs/XBINFO.svg)

**BASE** : BASE域段保存当前ACR上跨ACR调用至当前ACR的入口基址，要求32字节对齐，完整的入口地址为：BASE<<5。BASE指向的表格内存内容不超过一个4KB的页，不能跨越两个4KB页的对齐边界。超过的部分会被忽略。

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | XBINFO_ACR0  | 0x0f30 |
| ACR1   | XBINFO_ACR1  | 0x1f30 |
| ACR2   | XBINFO_ACR2  | 0x2f30 |
| ACR3   | XBINFO_ACR3  | 0x3f30 |
| ACR4   | XBINFO_ACR4  | 0x4f30 |
| ACR5   | XBINFO_ACR5  | 0x5f30 |
| ACR6   | XBINFO_ACR6  | 0x6f30 |
| ACR7   | XBINFO_ACR7  | 0x7f30 |
| ACR8   | XBINFO_ACR8  | 0x8f30 |
| ACR9   | XBINFO_ACR9  | 0x9f30 |
| ACR10  | XBINFO_ACR10  | 0xaf30 |
| ACR11  | XBINFO_ACR11  | 0xbf30 |
| ACR12  | XBINFO_ACR12  | 0xcf30 |
| ACR13  | XBINFO_ACR13  | 0xdf30 |
| ACR14  | XBINFO_ACR14  | 0xef30 |
| ACR15  | XBINFO_ACR15  | 0xff30 |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
