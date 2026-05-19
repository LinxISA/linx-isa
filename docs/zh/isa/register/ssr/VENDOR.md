# VENDOR

供应商ID寄存器（Vendor ID Register）用于存储处理器的供应商信息，以及标识不同制造商的核心或平台。

![VENDOR](../../../figs/bitfield/svg/Sysregs/VENDOR.svg)

**Vendor ID** : 代表当前处理器有效的制造商ID。

**Family ID** ：代表当前处理器的有效系列。

**Model ID** : 代表当前处理器的有效模型。

## 备注

该寄存器是**只读的(RO)**，其SSRID为**0x0022**。
