# 矩阵数据块

矩阵数据块指令是为硬件提供的专用矩阵运算接口，用于驱动底层CUBE计算单元执行高效、并行的张量/矩阵运算。该类指令以分形为基本粒度，将存储在Tile寄存器中的矩阵划分为多个分形结构进行数据计算，从而支持高维度、大规模并行化的矩阵运算处理。

矩阵数据块属于仅有块头而无块体的指令类型，其内部不可编程也不可拆解。软件仅需通过矩阵数据块头指令指定输入矩阵所在的Tile寄存器及其行列信息等参数。硬件在解析这些参数后将指令发至CUBE运算单元，由该单元完成相应的矩阵运算。

## 块类型特征

- 矩阵数据块**仅支持Fall跳转方式**
- 矩阵数据块允许访问 全局寄存器GGPR以及Tile寄存器，**不允许访问内存和系统寄存器SSR**。
- 矩阵数据块一个块最多允许读8个Tile寄存器，写4个tile寄存器。
- 矩阵运算结果**只允许输出到ACC寄存器**，并通过一条特定指令ACCCVT写到通用Tile寄存器中。
- 矩阵数据块无块体，**不允许使用B.TEXT指令**

## 指令列表

| TileOp  |   说明    |
|---------|------------|
| [TMATMUL](../../header/tileblock/TMATMUL.md)            | 矩阵乘指令，A矩阵 乘 B矩阵，结果写到ACC寄存器   |
| [TMATMUL.BIAS](../../header/tileblock/TMATMUL.BIAS.md)  | 矩阵乘加指令，A矩阵 乘 B矩阵，再加C矩阵，结果写到ACC寄存器    |
| [TMATMUL.ACC](../../header/tileblock/TMATMUL.ACC.md)    | 矩阵乘累加指令，A矩阵 乘 B矩阵，结果累加到ACC寄存器  |
| [TMATMULMX](../../header/tileblock/TMATMULMX.md)             | 缩放矩阵乘，结果写到ACC寄存器 |
| [TMATMULMX.BIAS](../../header/tileblock/TMATMULMX.BIAS.md)   | 缩放矩阵乘，加偏置矩阵，结果写到ACC寄存器 |
| [TMATMULMX.ACC](../../header/tileblock/TMATMULMX.ACC.md)     | 缩放矩阵乘，结果矩阵累加到ACC寄存器 |
| [ACCCVT](../../header/tileblock/ACCCVT.md)              | 将ACC寄存器内的数据搬移至通用Tile寄存器 |
| [TGEMV](../../header/tileblock/TGEMV.md)                | 通用矩阵-向量乘法，结果写到ACC寄存器 |
| [TGEMV.BIAS](../../header/tileblock/TGEMV.BIAS.md)      | 通用矩阵-向量乘法，带偏置加法，结果写到ACC寄存器 |
| [TGEMV.ACC](../../header/tileblock/TGEMV.ACC.md)        | 通用矩阵-向量乘法，结果累加到ACC寄存器 |
| [TGEMVMX](../../header/tileblock/TGEMVMX.md)            | 通用缩放矩阵-向量乘法，结果写到ACC寄存器 |
| [TGEMVMX.BIAS](../../header/tileblock/TGEMVMX.BIAS.md)  | 通用缩放矩阵-向量乘法，带偏置加法，结果写到ACC寄存器 |
| [TGEMVMX.ACC](../../header/tileblock/TGEMVMX.ACC.md)    | 通用缩放矩阵-向量乘法，结果累加到ACC寄存器 |

我们提供了一个特殊的[Tile寄存器](../../register/common/tilereg.md) - **ACC**，它主要用于降低CUBE单元中乘累加操作的数据读写带宽。该寄存器是CUBE单元内一块私有的存储区域，并且只能通过矩阵运算指令和ACCCVT指令访问。

![acc](../../../figs/isa/arch/acc.png){ width="600" }

示例：
```asm
    TMATMUL <M:64, N:32, K:64, FP32> T#4, T#3, ->ACC<16KB>
    TMATMUL.ACC <M:64, N:32, K:64, FP32> T#1, T#2, ACC, ->ACC<8KB>
    ACCCVT NORM <Row:64, Col:64, FP32> ACC, ->T<16KB>
```

上述示例中，`TMATMUL`指令写到ACC寄存器，然后被后序的`TMATMUL.ACC`指令读取并用于乘累加运算，最后通过`ACCCVT`指令将结果搬运至T类型Tile寄存器。

## 输入要求

需注意的是，由于CUBE运算单元基于一种固化实现的脉动阵列结构执行矩阵运算，因此输入矩阵必须按照指定的存储布局进行组织，否则硬件无法确保运算的正确性。

矩阵乘运算中，要求输入的多个矩阵（这里分别用Matrix A、Matrix B和Matrix C表示）必须保证以如下的布局进行存储。

矩阵乘运算：

![matmul](../../../figs/isa/inst/matmul.png)

矩阵乘累加运算：

![matmadd](../../../figs/isa/inst/matmadd.png)

其中，矩阵A和矩阵C必须以`大N小z`的布局进行存储，矩阵B必须以`大Z小n`的布局进行存储。布局介绍请见[存储布局](../../register/common/tilereg.md)。

假设S0和K0分别为K维度分形大小的字节数和元素个数。不同的硬件实现，S0的大小可以不同。那么：

- 矩阵A的分形矩阵大小是`16 x K0`的。
- 矩阵B的分形矩阵大小是`K0 x 16`的。
- 矩阵C的分形矩阵大小是`16 x 16`的。

K0可以通过以下公式计算得到：
```c
    K0 = S0 / sizeof(DataType);   # DataType表示元素数据类型
```

如果没有特殊要求，基于本指令集实现的硬件建议以如下标准实施：

- A矩阵和B矩阵的一个分形大小为 **512Byte**，对应S0大小为 **32Byte**。
- C矩阵的一个分形大小随着内部元素的位宽不同而变化。如果矩阵内元素是4byte宽，那么分形大小是**1024Byte**（16x16x4 byte）；如果元素是2byte宽，那么分形大小是**512Byte**。

另外，矩阵运算前要求硬件**将所有元素转换为FP32或INT32格式**，然后再进行运算。对于浮点型输入，那么统一转换为FP32格式计算，如果是整型输入，那么统一转换为INT32格式计算。

## 输出要求

灵犀指令集中，矩阵运算后需要通过ACCCVT指令继续进行一系列的随路处理，例如激活、量化、元素级运算等。如果统一从ACC寄存器获取数据再做进一步处理，可以很大程度的简化硬件实现。因此要求矩阵运算结果 **只允许输出到ACC寄存器**。

另一方面，根据输入矩阵的格式要求，那么结果矩阵一定是以`大N小z`的布局进行存储的。又因为以FP32或INT32格式进行运算，因此每个分形的大小固定为 **1024Byte**（16x16x4 byte）。

对矩阵运算的输出要求总结如下：

| 类型 | 要求 | 
|------|-----------|
| 目的寄存器 | 只允许输出到ACC寄存器 |
| 输出布局   | 大N小z格式         |
| 分形大小   | 1024Byte          |
