# 0.52版本更新

更新日期：2025年6月30日

指令编码设计文档网页版路径请见[LinxISA Encoding-0.52](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:100994184997)

## 一、版本更新背景

灵犀指令集在0.50和0.51版本中完成了标量和矢量运算指令的补充。0.52版本的更新重点是扩展和完善与张量相关的计算指令，旨在进一步提升大规模预训练模型等AI场景下的运算能力。通过在0.5版本基础上构建的块指令框架，灵犀指令集实现了对数据块操作（TileOP）的补充，增强了对不同大小、不同维度和格式的数据块的支持。

本次更新引入了数据块指令（TileOP）这一新概念，使得硬件能够对各种不同的计算块进行优化管理，从而更高效地处理多维张量的运算，尤其是在处理大规模数据集和复杂模型时。灵犀指令集通过对张量计算的扩展，特别是在分布式AI计算任务中的应用，进一步提升了灵犀指令集的灵活性和性能表现。

## 二、基本概念定义

随着数据块指令的引入，对于TileOP的实现还会涉及一些新的概念，具体如下：

- Tile: 数据块，指的是可被处理的最小计算单元。
- Tile Register: 存储数据块的基本硬件单元。
- Tile Operation (TileOP): 数据块指令，指的是对数据块进行处理和操作的指令。
- Tensor: 张量，通常由多维数据组成，具有固定的数据宽度和格式，可以进行切分（Tiling）为多个数据块。
- Tensor Operation: 张量计算，涵盖从element-wise计算到更复杂的矩阵乘法、抽取（Extract）、切分（Split）、合并（Concat）、转置（Transpose）等基本操作。它们构成了对张量的基本元计算。
- CodeGen（也叫MicroCodeEngine）：灵犀核的模板块生成单元。该单元通过接收模板块头来生成相应的指令序列。
- FixPipe: 不可拆解的块指令，通常由硬化管线执行，包括CUBE和SORT单元。

对于Tile的操作示例：
```c
  Tile <16,16,16> a;
  Tile <16,16,16> b;
  Tile <32,16,16> c;
  c = concat.row(a, b)    # 将两个Tile按照行维度拼接
```

新增指令的引入，能够更好地支持大规模AI运算中的张量切分与组合，提升了指令集的运算效率。

## 三、详细定义

灵犀指令集0.52版本通过引入模板块，扩展了对张量的元计算支持。这些模板块在汇编格式中表现为模板指令，或是带有块头但没有具体块体的宏指令。这些块指令被定义为数据块指令（Tile Block Instruction），进一步增强了灵犀指令集对大规模数据块计算的处理能力。本版本提供的数据块指令列表如下：

**分类一：矩阵运算**

| 数据块名称/TileOP | 说明 | 备注 |
|------------------|-------|-----------|
| MAMULB      | A矩阵 乘 B矩阵 |
| MAMULB.ACC  | A矩阵 乘 B矩阵，累加至C矩阵 |
| MAMULBT     | A矩阵 乘 B矩阵的转置 |
| MAMULBT.ACC | A矩阵 乘 B矩阵的转置，累加至C矩阵 |

**分类二：向量运算**

| 数据块名称/TileOP | 说明 | 备注 |
|------------------|-------|-----------|
| VCALL | 分离块，块体定义功能 |
| TADD | 两个数据块逐元素相加 | 
| TSUB | 两个数据块逐元素相减 | 
| TMUL | 两个数据块逐元素相乘 | 
| TDIV | 两个数据块逐元素相除 | 
| TMAX | 两个数据块逐元素比较最大值 | 
| TADDS | 数据块逐元素与标量相加 | 
| TSUBS | 数据块逐元素与标量相减 | 
| TMULS | 数据块逐元素与标量相乘 | 
| TDIVS | 数据块逐元素与标量相除 | 
| TMAXS | 数据块逐元素与标量比较最大值 | 
| TEXP | 数据块逐元素求自然指数 | 
| TSQRT | 数据块逐元素求平方根 | 
| TRECIP | 数据块逐元素求倒数 | 
| TABS | 数据块逐元素求绝对值 | 
| TCAST | 数据块逐元素数据格式转换 | 
| TROWSUM | 数据块 行求和归约 | 
| TROWMAX | 数据块 行最大值归约 | 
| TROWSUMEXP | 数据块 行求和归约 然后扩展 | 
| TROWMAXEXP | 数据块 行最大值归约 然后扩展 | 

**分类三：数据搬运**

| 数据块名称/TileOP | 说明 | 备注 |
|------------------|-------|-----------|
| MCALL    | 分离块，块体定义功能 |
| TCOPYIN  | 从内存ddr或remote向Tile Register拷贝 | 
| TCOPYOUT | 从Tile Register向内存ddr或remote拷贝 | 
| TCOPY    | Tile Register之间拷贝 | 

以上TileOP列表中，VCALL和MCALL用于定义分离块，硬件执行时分别发给Vector核和Memory核执行。其余TileOP定义为模版块。

所有数据块指令（TileOP）都可以使用一条完整的汇编格式表达，格式如下：
```asm
分离块：TileOP body_label, <LB0:reg/imm, LB1:reg/imm, LB2:reg/imm> SrcTile0, SrcTile1, SrcTile2, [BGetList], ->DstTileType<TileSize>, [BSetList]
模版块：TileOP <Row:reg/imm, Col:reg/imm, Dep:reg/imm, DataType> SrcTile0, SrcTile1, SrcTile2, [BGetList], ->DstTileType<TileSize>, [BSetList]
```
一条完整的汇编可以拆分成以下指令:

- BSTART.PAR：定义并行块指令起始位置以及本块实现的TileOP等。
- B.DIM：本块运算的矩阵或者数据块的维度信息。
- B.IOT：本块的Tile Register输入输出以及输出Tile的空间。
- B.IOR：本块的全局寄存器输入输出。
- B.TEXT： 块体位置信息。
