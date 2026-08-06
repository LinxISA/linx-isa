# 矩阵数据块

矩阵数据块指令是为硬件提供的专用矩阵运算接口，用于驱动底层CUBE计算单元执行高效、并行的张量/矩阵运算。该类指令以分形为基本粒度，将存储在Tile寄存器中的矩阵划分为多个分形结构进行数据计算，从而支持高维度、大规模并行化的矩阵运算处理。

矩阵数据块属于仅有块头而无块体的指令类型，其内部不可编程也不可拆解。软件仅需通过矩阵数据块头指令指定输入矩阵所在的Tile寄存器及其行列信息等参数。硬件在解析这些参数后将指令发至CUBE运算单元，由该单元完成相应的矩阵运算。

## 块类型特征

- 矩阵数据块**仅支持Fall跳转方式**
- 矩阵数据块允许访问 全局寄存器GGPR以及Tile寄存器，**不允许访问内存和系统寄存器SSR**。
- 矩阵数据块一个块最多允许读8个Tile寄存器，写4个tile寄存器。
- 每个矩阵操作都写入显式 Local 目的 Tile D。ACC 形式还读取显式 Local 累加输入 C；当 D 与 C 相同时，语义为读旧值、写新值。
- 矩阵数据块无块体，**不允许使用B.TEXT指令**

## 指令列表

| TileOp  |   说明    |
|---------|------------|
| [TMATMUL](../../header/tileblock/TMATMUL.md)            | 矩阵乘，写显式目的 D |
| [TMATMUL.BIAS](../../header/tileblock/TMATMUL.BIAS.md)  | 矩阵乘加显式偏置，写显式目的 D |
| [TMATMUL.ACC](../../header/tileblock/TMATMUL.ACC.md)    | 从显式累加输入 C 读值并写显式目的 D |
| [TMATMULMX](../../header/tileblock/TMATMULMX.md)             | 带行/列 scale 的矩阵乘，写显式目的 D |
| [TMATMULMX.BIAS](../../header/tileblock/TMATMULMX.BIAS.md)   | 带 scale 和偏置的矩阵乘，写显式目的 D |
| [TMATMULMX.ACC](../../header/tileblock/TMATMULMX.ACC.md)     | 带 scale 的矩阵乘累加，从 C 读并写 D |
| [TGEMV](../../header/tileblock/TGEMV.md)                | 矩阵-向量乘，写显式目的 D |
| [TGEMV.BIAS](../../header/tileblock/TGEMV.BIAS.md)      | 矩阵-向量乘加偏置，写显式目的 D |
| [TGEMV.ACC](../../header/tileblock/TGEMV.ACC.md)        | 矩阵-向量累加，从 C 读并写 D |
| [TGEMVMX](../../header/tileblock/TGEMVMX.md)            | 带 scale 的矩阵-向量乘，写显式目的 D |
| [TGEMVMX.BIAS](../../header/tileblock/TGEMVMX.BIAS.md)  | 带 scale 和偏置的矩阵-向量乘，写显式目的 D |
| [TGEMVMX.ACC](../../header/tileblock/TGEMVMX.ACC.md)    | 带 scale 的矩阵-向量累加，从 C 读并写 D |

PTO ISA 0.58 不存在隐藏的架构 ACC 状态，也没有 `ACCCVT` 操作。逻辑累加角色由普通 Local Tile 操作数承担，因此目的生命周期、别名和转换行为都由块描述符显式表达。

![acc](../../../figs/isa/arch/acc.png){ width="600" }

base 与 BIAS 形式由描述符指定 D 和全部矩阵/向量输入；ACC 形式额外指定累加输入 C。`D == C` 是定义良好的读旧值、写新值别名；否则读取 C 并独立更新 D。

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

在 v0.58 中，矩阵结果直接写入显式 Local 目的 Tile。后续激活、量化、布局转换或逐元素操作通过普通显式操作数读取该 Tile。

另一方面，根据输入矩阵的格式要求，那么结果矩阵一定是以`大N小z`的布局进行存储的。又因为以FP32或INT32格式进行运算，因此每个分形的大小固定为 **1024Byte**（16x16x4 byte）。

对矩阵运算的输出要求总结如下：

| 类型 | 要求 | 
|------|-----------|
| 目的寄存器 | 显式 Local 目的 Tile D |
| 输出布局   | 大N小z格式         |
| 分形大小   | 1024Byte          |
