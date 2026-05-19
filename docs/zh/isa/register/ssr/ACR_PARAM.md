# ACR_PARAM

ACRn LxLC参数寄存器（ACR Parameter Register）是 **只读的(RO)** 的系统寄存器，用于指定ARCn的LxLC参数。

![ACR_PARAM](../../../figs/bitfield/svg/Sysregs/ACR_PARAM.svg)

**EBS_SZ** 为ACRn的 `EBSTATE` 内存最大需要容纳多少个64位整数。

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | ACR_PARAM_ACR0  | 0x0f31 |
| ACR1   | ACR_PARAM_ACR1  | 0x1f31 |
| ACR2   | ACR_PARAM_ACR2  | 0x2f31 |
| ...   | ...  | ... |
| ACRn   | ACR_PARAM_ACRn  | 0xnf31 |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
