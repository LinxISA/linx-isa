# LCFR_EN

灵犀核特征使能寄存器（Linx Core Feature Enable Register）<br>
该寄存器启用或禁用处理器特定功能，例如并行块、浮点运算等，编译器根据该寄存器的设置生成兼容的代码。它是**可读写的(RW)**，但对于每个特定的位，只有特定的ACR才能写入。无权写入的ACR修改对应的位不会产生任何效果。

![LCFR_EN](../../../figs/bitfield/svg/Sysregs/LCFR_EN.svg)

所有字段的定义同[LCFR](../../../isa/register/ssr/LCFR.md)寄存器中定义

## 备注

该寄存器的SSRID为**0x0025**。
