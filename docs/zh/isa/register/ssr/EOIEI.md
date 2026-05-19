# EOIEI

中断结束寄存器（End of Interrupt Register）是 **只写的（WO）** 系统寄存器，用于指示中断处理结束，允许处理器返回到正常执行状态。

![EOIEI](../../../figs/bitfield/svg/Sysregs/EOIEI.svg)

- **IntID**：当此字段被写入，LxLC将删除[IPENDING](./IPENDING.md)寄存器中相应的挂起中断的挂起位。

此处列出所有可用作IntID的有效值：

- 0, ACR0_EI, Accepted only from EOIEI_ACR0。
- 1, ACR0_TI, Accepted only from EOIEI_ACR0。
- 2, ACR1_EI, Accepted only from EOIEI_ACRn where n p>= 1。
- 3, ACR1_TI, Accepted only from EOIEI_ACRn where n p>= 1。

如果写入其他值，LxLC则不执行任何操作。

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | EOIEI_ACR0  | 0x0f0a |
| ACR1   | EOIEI_ACR1  | 0x1f0a |
| ACR2   | EOIEI_ACR2  | 0x2f0a |
| ...   | ...  | ... |
| ACRn   | EOIEI_ACRn  | 0xnf0a |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
