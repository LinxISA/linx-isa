# FUTO

异常修复接管寄存器（Fixup Takeover Register）是 **可读写的(RW)** 系统寄存器，用于配置修复块接管。

![FUTO](../../../figs/bitfield/svg/Sysregs/FUTO.svg)

该寄存器存储异常修复接管的状态，帮助操作系统处理和修复异常场景。

其格式定义如下：

| futo bits | 汇编符号| 异常原因                           | 描述                   |
| --------- | --------|-------------------------- | ---------------------- |
| 0         |  LF  |E_DATA(1)-EC_LOAD(0)               | 内存加载(Load)访问错误 |
| 1         |  LMA |E_DATA(1)-EC_MISALIGNED(1)         | 内存加载(Load)未对齐   |
| 2         |  SF  |E_DATA(1)-EC_STORE_A_ACCESS(3)     | 内存写(Store)访问错误  |
| 3         |  SMA |E_DATA(1)-EC_STORE_A_MISALIGNED(4) | 内存写(Store)未对齐    |
| 4         |  A   |ASSERT EXCEPTIONS                  | 触发assert异常         |

- 当该位被设置时，相应的异常将由相应的ACR的异常处理程序接管。
- 系统复位时，默认情况下，所有futo位都设置为0。

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | FUTO_ACR0  | 0x0f06 |
| ACR1   | FUTO_ACR1  | 0x1f06 |
| ACR2   | FUTO_ACR2  | 0x2f06 |
| ...   | ...  | ... |
| ACRn   | FUTO_ACRn  | 0xnf06 |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
