# 0.52 version update

Update date: June 30, 2025

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-0.52](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:100994184997)

## 1. Version update background

LinxISA completes the complement of scalar and vector operation instructions in versions 0.50 and 0.51. The update of version 0.52 focuses on expanding and improving the computing instructions related to tensor, aiming to further improve the computing power in AI scenarios such as large-scale pre-training models. Through the block instruction framework built on the basis of version 0.5, LinxISA implements the supplement of data block operations (TileOP) and enhances the support for data blocks of different sizes, different dimensions and formats.

This update introduces the new concept of data block instruction (TileOP), which enables the hardware to optimize the management of various calculation blocks, thereby processing multi-dimensional tensor operations more efficiently, especially when processing large-scale data sets and complex models. LinxISA further improves the flexibility and performance of LinxISA by extending the computing of tensor, especially its application in distributed AI computing tasks.

## 2. Definition of basic concepts

With the introduction of data block instruction, the implementation of TileOP will also involve some new concepts, as follows:

- Tile: Data block refers to the smallest computing unit that can be processed.
- Tile Register: The basic hardware unit for storing data blocks.
- Tile Operation (TileOP): Data block instruction refers to instructions for processing and operating data blocks.
- Tensor: tensor, usually consists of multi-dimensional data, has fixed data width and format, and can be segmented (Tiling) into multiple data blocks.
- Tensor Operation: tensor calculation, covering basic operations from element-wise calculation to more complex matrix multiplication, extraction (Extract), split (Split), merge (Concat), transpose (Transpose) and other basic operations. They constitute the basic element calculation for tensor.
- CodeGen (also called MicroCodeEngine): template block generation unit of Linx core. The unit generates the corresponding instruction sequence by receiving the template block header.
- FixPipe: Non-detachable block instruction, usually performed by hardened pipelines, including CUBE and SORT units.

Operation example for Tile:
```c
  Tile <16,16,16> a;
  Tile <16,16,16> b;
  Tile <32,16,16> c;
  c = concat.row(a, b)    # 将两个Tile按照行维度拼接
```

The introduction of new instructions can better support tensor segmentation and combination in large-scale AI operations, improving the computing efficiency of the instruction set.

## 3. Detailed definition

LinxISA version 0.52 extends metacomputing support for tensor by introducing template block. These template block appear as template instructions in assembly format, or macro instructions with header but no specific body. These block instruction are defined as data block instruction (Tile Block Instruction), which further enhances LinxISA's processing capabilities for large-scale data block calculations. The list of data block instruction provided in this version is as follows:

**Category 1: Matrix Operations**

| Data block name/TileOP | Description | Remarks |
|------------------|-------|-----------|
| MAMULB | A matrix times B matrix |
| MAMULB.ACC | A matrix multiplied by B matrix, accumulated to C matrix |
| MAMULBT | A matrix multiplied by transpose of B matrix |
| MAMULBT.ACC | A matrix multiplied by the transpose of B matrix, accumulated to C matrix |**Category 2: vector operation**

| Data block name/TileOP | Description | Remarks |
|------------------|-------|-----------|
| VCALL | Separation block, body definition function |
| TADD | Element-wise addition of two data blocks |
| TSUB | Subtract two data blocks element by element |
| TMUL | Element-wise multiplication of two data blocks |
| TDIV | Element-wise division of two data blocks |
| TMAX | Compare the maximum value of two data blocks element by element |
| TADDS | Add data block element by element with scalar |
| TSUBS | Data block is subtracted element by element from scalar |
| TMULS | Data block element-wise multiplication with scalar |
| TDIVS | Data block element-wise division by scalar |
| TMAXS | Data block element-by-element comparison with scalar for maximum value |
| TEXP | Find the natural exponent of a data block element by element |
| TSQRT | Find the square root of a data block element by element |
| TRECIP | Find the reciprocal of data block element by element |
| TABS | Find the absolute value of data block element by element |
| TCAST | Data block element-by-element data format conversion |
| TROWSUM | Data block row sum reduction |
| TROWMAX | Data block row maximum reduction |
| TROWSUMEXP | Data block row sum reduction then expansion |
| TROWMAXEXP | Data block row maximum reduction then expansion |

**Category Three: Data Transfer**

| Data block name/TileOP | Description | Remarks |
|------------------|-------|-----------|
| MCALL | Separation block, body definition function |
| TCOPYIN | Copy from memory ddr or remote to Tile Register |
| TCOPYOUT | Copy from Tile Register to memory ddr or remote |
| TCOPY | Copy between Tile Registers |

In the above TileOP list, VCALL and MCALL are used to define separate blocks, which are sent to the Vector core and Memory core for execution respectively during hardware execution. The remaining TileOP is defined as template block.

All data block instruction (TileOP) can be expressed using a complete assembly format, the format is as follows:
```asm
分离块：TileOP body_label, <LB0:reg/imm, LB1:reg/imm, LB2:reg/imm> SrcTile0, SrcTile1, SrcTile2, [BGetList], ->DstTileType<TileSize>, [BSetList]
ZXTERMZH36QXZ：TileOP <Row:reg/imm, Col:reg/imm, Dep:reg/imm, DataType> SrcTile0, SrcTile1, SrcTile2, [BGetList], ->DstTileType<TileSize>, [BSetList]
```
A complete assembly can be broken down into the following instructions:

- BSTART.PAR: Defines the starting position of parallel block instruction and the TileOP implemented by this block, etc.
- B.DIM: Dimension information of the matrix or data block operated by this block.
- B.IOT: Tile Registerinput/output of this block and the space for output Tile.
- B.IOR: Global register input/output of this block.
- B.TEXT: body location information.