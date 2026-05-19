# IPENDING

中断挂起寄存器（Interrupt Pending Register）是 **只读的(RO)** 系统寄存器，用于显示对ACRn可见的所有挂起中断，以确定处理器在何时响应中断。

![IPENDING](../../../figs/bitfield/svg/Sysregs/IPENDING.svg)

其中：

- E位映射到外部中断
- T位映射到定时器中断
- I位映射到核间中断（IPI）

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | IPENDING_ACR0  | 0x0f08 |
| ACR1   | IPENDING_ACR1  | 0x1f08 |
| ACR2   | IPENDING_ACR2  | 0x2f08 |
| ...   | IPENDING_ACR3  | 0x3f08 |
| ACR4   | IPENDING_ACR4  | 0x4f08 |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
