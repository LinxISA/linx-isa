# TEXTRACT

## 说明

**数据块提取（Tile Extract）**

`TEXTRACT` 从源 Tile 的指定偏移位置 `(indexRow, indexCol)` 处提取一个子 Tile，结果写入输出 Tile 中。

实现伪代码示意如下：
```pseudocode
// 子 Tile 提取操作
for r in 0..(DstValidRow-1):                           // 遍历目标所有行
  for c in 0..(DstValidCol-1):                         // 遍历目标所有列
    dst[r, c] = src[indexRow + r, indexCol + c]          // 从源 Tile 偏移处复制
```

---

## 汇编语法

```asm
TEXTRACT Layout, <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, [RegSrc0, RegSrc1], ->DstTile<Size>
```

## 汇编符号

- **Layout**：指示数据移动过程中存储布局的变换方式，支持 `NORM`、`NZ2ND`、`NZ2DN` 等。
- **ValidCol**：输出 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：输出 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：输出 Tile 的总行数，通过公式计算：`Row = DstTileSize / (Col × sizeof(DataType))`。
- **DataType**：输入/输出 Tile 元素的数据格式，支持类型见下表。
- **PadValue**：输出 Tile 无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。
- **SrcTile**：输入 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **RegSrc0**：提取起始列索引 IdxCol（`uint16_t`），由 GGPR 提供。
- **RegSrc1**：提取起始行索引 IdxRow（`uint16_t`），由 GGPR 提供。
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

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `TEXTRACT, DataType`
- [B.ATTR](../../header/B.ATTR.md) `Layout, PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc0, RegSrc1`

## 约束条件

- **边界约束**：
    - `indexRow + ValidRow <= SrcTile::Row`
    - `indexCol + ValidCol <= SrcTile::Col`
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **数据类型**：`SrcTile::DataType == DstTile::DataType`
- **存储布局**：必须是行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TEXTRACT NORM, <LB0:16, LB1:8, FP32>, T#1.reuse, [a0, a1], ->T<512B>
```

1. **操作内容**
    - 从 `T#1` Tile 的 `(a1, a0)` 偏移处提取 8×16 的子 Tile
    - 输出：结果存入新的 `T` 队列 Tile 寄存器
2. **数据处理范围**
    - 有效列数 `16`（由 `LB0:16` 指定）
    - 有效行数 `8`（由 `LB1:8` 指定）
3. **偏移**
    - 起始列索引由 `a0` 指定，起始行索引由 `a1` 指定
4. **数据格式**
    - 使用 `32 位单精度浮点数`（`FP32`）格式

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
