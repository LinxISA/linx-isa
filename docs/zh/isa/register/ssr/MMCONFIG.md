# MMCONFIG

内存管理配置寄存器（Memory Management Configuration Register）用于配置内存管理单元的行为，例如分页大小、地址空间范围等。编译器根据该寄存器生成优化的内存管理代码。

![MMCONFIG](../../../figs/bitfield/svg/Sysregs/MMCONFIG.svg)

- **M**：层的模式或数量。层数转换模式选择器。该模式被定义并与已实现的模式绑定，否则重置为2'b00。

|  M  |    mode        |
|-----|----------------|
| 00  |  VA39 or VA36  |
| 01  |  VA48 or VA44  |
| 10  |  VA57 or VA52  |
| 11  |  Reserved  |

- **Q**: 四字页表使能。表示有效页面模式和VA切片模式。连接到实现的内容，否则重置为1'b1。
    - 0：8 Byte（Longword 长字页表条目 (LPTE)
    - 1：16 Byte（Quadword）四字页表条目 (QPTE)

- **HU**：（保留字段）硬件用于更新pte的a/d位。这是为了指定pte.A或pte.D的更新是基于硬件或软件的。
    - 0：A/D 字段更新是基于软件的.
    - 1：A/D 字段更新是基于硬件的.

- **EN**：使能。启用地址转换。重置0。VA切片选项，MMCONFIG.NL和MMCONFIG.Q字段定义上的预期VA切片选项。

| Virtual Address Mode | Virtual Address Width | MMCONFIG.Q | MMCONFIG.NL | Levels of Translation | Virtual Address Space |
|----------------------|-----------------------|------------|-------------|-----------------------|-----------------------|
|  VA36  |  36  |  1  |  0  |  3  |  64G  |
|  VA39  |  39  |  0  |  0  |  3  |  512G  |
|  VA44  |  44  |  1  |  1  |  4  |  16T  |
|  VA48  |  48  |  0  |  1  |  4  |  256T  |
|  VA52  |  52  |  1  |  2  |  5  |  4P  |
|  VA57  |  57  |  0  |  2  |  5  |  128P  |

## 备注

该寄存器的SSRID为`0x1f11`,其存在于supervisor, hypervisory, machinery级权限，但不在用户级权限使用。
