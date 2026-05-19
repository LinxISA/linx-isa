# ECSTATE

异常状态寄存器(Exception State Register)保存当前异常状态，用于异常和中断处理。软件可以根据该寄存器了解异常发生时的处理流程。

![ECSTATE](../../../figs/bitfield/svg/Sysregs/ECSTATE.svg)

## BI

**BI（Block Interrupted）** 是块体内触发异常的标志位，用于标识异常服务请求SERVICE_REQUEST是否发生在块体内。如果发生在块体内则此位被置1，否则清除。

软件可根据BI位是否置位，决定是否保存以及恢复块内状态。

其他所有字段与[CSTATE](./ECSTATE.md)寄存器的定义相同。

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | ECSTATE_ACR0  | 0x0f00 |
| ACR1   | ECSTATE_ACR1  | 0x1f00 |
| ACR2   | ECSTATE_ACR2  | 0x2f00 |
| ...   | ...  | ... |
| ACRn   | ECSTATE_ACRn  | 0xnf00 |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
