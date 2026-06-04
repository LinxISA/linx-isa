# TTRANS

## 说明

**数据块转置（Tile Transpose）**

`TTRANS` 对输入 Tile 执行矩阵转置操作，将源 Tile 的行变为目标 Tile 的列，结果写入输出 Tile 中。

实现伪代码示意如下：
```pseudocode
// 矩阵转置操作
for r in 0..(SrcValidRow-1):                           // 遍历源所有行
  for c in 0..(SrcValidCol-1):                         // 遍历源所有列
    dst[c, r] = src[r, c]                                // 行列交换
```

---

## 汇编语法

```asm
TTRANS <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输出 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：输出 Tile 的总列数（可缺省，默认值：等于 `ValidRow`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：输出 Tile 的总行数，通过公式计算：`Row = DstTileSize / (Col × sizeof(DataType))`。
- **DataType**：输入/输出 Tile 元素的数据格式，支持类型见下表。
- **PadValue**：输出 Tile 无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。
- **SrcTile**：输入 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：输出 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输出。
- **Size**：输出 Tile 寄存器的空间大小（有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)）。

本指令支持数据类型（DataType）如下表所示：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | S64, U64, FP64 |
| b32 | S32, U32, FP32, TF32, HF32 |
| b16 | S16, U16, FP16, BF16 |
| b8  | S8,  U8,  FP8(E4M3, E5M2) |

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `TTRANS, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **形状关系**：
    - `DstTile::ValidRow == SrcTile::ValidCol`
    - `DstTile::ValidCol == SrcTile::ValidRow`
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **数据类型**：`SrcTile::DataType == DstTile::DataType`
- **存储布局**：输出为行主序（RowMajor）。
- **对齐**：源 Tile 的行列建议 32 字节对齐以获得最佳性能。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TTRANS <LB0:32, LB1:16, FP32>, T#1.reuse, ->T<2KB>
```

1. **操作内容**
    - 将 `T#1` Tile（16×32）转置为 32×16
    - 输出：结果存入新的 `T` 队列 Tile 寄存器
2. **数据处理范围**
    - 源有效列数 `32`（转置后变为目标有效行数）
    - 源有效行数 `16`（转置后变为目标有效列数）
3. **数据格式**
    - 使用 `32 位单精度浮点数`（`FP32`）格式
4. **输出**
    - `T<2KB>`：32 行 × 16 列 × 4 字节 = 2KB

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
