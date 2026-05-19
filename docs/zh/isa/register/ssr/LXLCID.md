# LXLCID

灵犀逻辑核ID寄存器（Linx Logical Core ID Register）保存着当前逻辑核的唯一标识，用于多核调度和核间通讯。

![LXLCID](../../../figs/bitfield/svg/Sysregs/LXLCID.svg)

编译器可利用该寄存器优化核级任务调度。

## 备注

该寄存器是**只读的(RO)**，其SSRID为**0x0021**。
