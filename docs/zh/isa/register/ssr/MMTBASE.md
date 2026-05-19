# MMTBASE

内存管理翻译库寄存器（Memory Management Translation Base Register）存储着内存管理单元的翻译库基地址，用于进行虚拟地址到物理地址的转换。

![MMTBASE](../../../figs/bitfield/svg/Sysregs/MMTBASE.svg)

- **[1:0]CONST_0**：作为地址转换模式的选择器，当前从位0开始作为常量值。常量值与TN0PB一起工作，形成 16 KB对齐的基节点。（2'b00：启用地址转换模式。）
- **[39:2]TN0PB**：转换节点0指针，基页（级别0页）是异常级别物理页的基地址，该页应对齐 16 KB。基页的物理地址计算如下且最多将52位分配给物理基页。

    `PA = zero_extend_to_64b({MMTBASE.TN0PB,14’d0})`

- **[63:40]ASID**：24位的应用程序空间标识符。实际位数是实现定义的。所有实现的位都从LSB开始连续分组。未实现的位都硬连线到0。对未实现的顶部位的写入将被忽略。例如，如果实现位=8，则合法集为[0..255]，ASID的16个顶部位都硬连线到0。

## 备注

该寄存器的SSRID为`0x1f10`, 其存在于supervisor, hypervisory, machinery权限，但不在用户级权限使用。
