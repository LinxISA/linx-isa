# TR

线程私有寄存器(Thread Register)包含TR1和TR2两个SSR，为轻核用户态自定义的系统寄存器，且每个线程都拥有独立的一个。

**TR1**

![TR1](../../../figs/bitfield/svg/Sysregs/TR1.svg)

**TR2**

![TR2](../../../figs/bitfield/svg/Sysregs/TR2.svg)

## 备注

该寄存器为轻核自定义的 **可读写的(RW)** 系统寄存器，其中TR1寄存器的SSRID为**0x0800**，TR2寄存器的SSRID为**0x0801**。
