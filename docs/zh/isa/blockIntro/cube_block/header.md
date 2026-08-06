# 块头定义

矩阵数据块的块头需要定义执行哪类矩阵运算操作、输入矩阵的尺寸和输入输出的Tile寄存器等信息。

## 汇编格式

```asm
TileOp <LB0:arg0, LB1:arg1, LB2:arg2, DataType>, SrcTile0<.reuse>, ..., SrcTile7<.reuse>, DepSrc0, DepSrc1, DepSrc2, 
                                     ->DstTile0<TileSize0>, ..., DstTile3<TileSize3>, DepDst
```

各参数说明如下：

| 参数 | 说明 | 是否可选 |
|------|------|---------|
| **TileOp** | 选择 v0.58 的 12 个 TMATMUL/TGEMV base、BIAS 或 ACC 操作之一 | 否  |
| **LB0** | 输入矩阵的行或列参数，具体见特定指令介绍。arg0可以通过（`全局寄存器`、`立即数`或`全局寄存器加立即数`）参数设置。 | 是，默认为1 |
| **LB1** | 输入矩阵的行或列参数，具体见特定指令介绍。arg1可以通过（`全局寄存器`、`立即数`或`全局寄存器加立即数`）参数设置。 | 是，默认为1 |
| **LB2** | 输入矩阵的行或列参数，具体见特定指令介绍。arg2可以通过（`全局寄存器`、`立即数`或`全局寄存器加立即数`）参数设置。 | 是，默认为1 |
| **DataType** | 输入元素的数据格式，包括FP32, FP16, S16等 | 是 |
| **SrcTile0, ..., SrcTile7** | 分别指示最多8个输入的Tile寄存器。 | 是 |
| **reuse** | 当本指令执行结束后相应的输入Tile寄存器不允许被释放则需要增加该标识。如无此标识，则表示允许硬件释放本寄存器。 | 是 |
| **DstTile0, ..., DstTile3** | 指定显式 Local 输出 Tile；ACC 形式还需指定显式 Local 累加输入 C | 是 |
| **TileSize0, ..., TileSize3** | 分别指示每个输出Tile寄存器的空间大小，可以通过一个 `立即数`或者`全局寄存器`传参。 | 取决于DstTile |
| **DepSrc0, DepSrc1, DepSrc2** | 表示本块指令最多显式记录 3 个前序 `D` 依赖槽位。 | 是 |
| **DepDst** | 表示本块指令对后序引用该标识的块指令的屏障。 | 是 |

## 编码方式

一条完整矩阵数据块指令块头需要拆分成以下多条指令进行编码，其中包括：

- 命名块头：`BSTART.TMATMUL DataTypeA`、`BSTART.TMATMUL.BIAS DataTypeA`、
  `BSTART.TMATMUL.ACC DataTypeA`、`BSTART.TMATMULMX DataTypeA`、
  `BSTART.TMATMULMX.BIAS DataTypeA`、`BSTART.TMATMULMX.ACC DataTypeA`、
  `BSTART.TGEMV DataType`、`BSTART.TGEMV.BIAS DataType`、
  `BSTART.TGEMV.ACC DataType`、`BSTART.TGEMVMX DataType`、
  `BSTART.TGEMVMX.BIAS DataType`、`BSTART.TGEMVMX.ACC DataType`
- [B.DATR](../../header/B.DATR.md) Layout.{canon, normal}, DataType
- [B.DIM](../../header/B.DIM.md) reg, imm, ->LB0
- [B.DIM](../../header/B.DIM.md) reg, imm, ->LB1
- [B.DIM](../../header/B.DIM.md) reg, imm, ->LB2
- [B.IOT](../../header/B.IOT.md) SrcTile0<.reuse>, SrcTile1<.reuse>, ->DstTile0< TileSize0>
- ...
- [B.IOT](../../header/B.IOT.md) SrcTile6<.reuse>, SrcTile7<.reuse>, last, ->DstTile3< TileSize3>

其中，CUBE 命名块头共享 BSTART.CUBE 编码族。只有表中的 12 个命名函数
合法；未分配的 Function 均为非法指令，不存在可执行的泛化 `BSTART.CUBE`
汇编形式。

其中，BSTART.CUBE 编码族格式如下：

![BSTART.CUBE](../../../figs/bitfield/svg/BlockHeader_32bit/BSTART.CUBE.svg)

其中，function字段用于编码具体的矩阵运算/FIXPIPE指令。编码方式如下：

| Mode | Function | 操作             |
|------|----------|------------------|
| 0    | 0        | [TMATMUL](../../header/tileblock/TMATMUL.md)               |
| 0    | 1        | [TMATMUL.BIAS](../../header/tileblock/TMATMUL.BIAS.md)     |
| 0    | 2        | [TMATMUL.ACC](../../header/tileblock/TMATMUL.ACC.md)       |
| 0    | 3        | 预留编码              |
| 0    | 4        | [TMATMULMX](../../header/tileblock/TMATMULMX.md)             |
| 0    | 5        | [TMATMULMX.BIAS](../../header/tileblock/TMATMULMX.BIAS.md)   |
| 0    | 6        | [TMATMULMX.ACC](../../header/tileblock/TMATMULMX.ACC.md)     |
| 0    | 7        | 预留编码        |
| 0    | 8-15     | 预留编码          |
| 0    | 16       | [TGEMV](../../header/tileblock/TGEMV.md)                |
| 0    | 17       | [TGEMV.BIAS](../../header/tileblock/TGEMV.BIAS.md)      |
| 0    | 18       | [TGEMV.ACC](../../header/tileblock/TGEMV.ACC.md)        |
| 0    | 19       | 预留编码        |
| 0    | 20       | [TGEMVMX](../../header/tileblock/TGEMVMX.md)            |
| 0    | 21       | [TGEMVMX.BIAS](../../header/tileblock/TGEMVMX.BIAS.md)  |
| 0    | 22       | [TGEMVMX.ACC](../../header/tileblock/TGEMVMX.ACC.md)    |
| 0    | 23-31    | 预留编码        |

DataType字段编码方式如下：

| 编码 | 数据类型 | 编码 | 数据类型 | 编码 | 数据类型 | 编码 | 数据类型 |
|------|----------|------|----------|------|----------|------|----------|
| 0    | FP64     | 8    | E5M2     | 16   | S64      | 24   | U64      |
| 1    | FP32     | 9    | E3M2     | 17   | S32      | 25   | U32      |
| 2    | TF32     | 10   | E2M3     | 18   | S16      | 26   | U16      |
| 3    | HF32     | 11   | E2M1x2   | 19   | S8       | 27   | U8       |
| 4    | FP16     | 12   | E1M2x2   | 20   | S4x2     | 28   | U4x2     |
| 5    | BF16     | 13   | E8M0     | 21   | reserve  | 29   | reserve  |
| 6    | HiF8     | 14   | HiF4x2   | 22   | reserve  | 30   | reserve  |
| 7    | E4M3     | 15   | reserve  | 23   | reserve  | 31   | invalid  |
