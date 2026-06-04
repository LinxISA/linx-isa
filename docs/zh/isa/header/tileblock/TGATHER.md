# TGATHER

## 说明

**数据块聚集（Tile Gather）**

`TGATHER` 使用索引 Tile 从源 Tile 中收集/选择元素，结果写入输出 Tile 中。还支持基于编译时掩码模式或基于比较的聚集变体。

实现伪代码示意如下：
```pseudocode
// 基于索引的聚集操作
for r in 0..(ValidRow-1):                              // 遍历所有行
  for c in 0..(ValidCol-1):                            // 遍历所有列
    idx = indices[r, c]                                   // 获取索引
    dst[r, c] = src[idx, c]                               // 根据索引从源中选择元素
```

---

## 汇编语法

```asm
TGATHER <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, IdxTile<.reuse>, ->DstTile<Size>
```

## 汇编符号

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
- **IdxTile**：索引 Tile 寄存器，元素类型为 `U32`。
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

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TGATHER, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, IdxTile<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **索引范围**：索引值必须小于 `SrcTile::ValidRow`，否则结果由硬件实现定义。
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **数据类型**：`SrcTile::DataType == DstTile::DataType`；`IdxTile::DataType == U32`。
- **存储布局**：必须是行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TGATHER <LB0:32, LB1:16, FP32>, T#1.reuse, U#2.reuse, ->T<2KB>
```

1. **操作内容**
    - 使用 `U#2` 中的索引从 `T#1` 中聚集 16×32 个元素
    - 输出：结果存入 `T` 队列 Tile 寄存器
2. **数据处理范围**
    - 输出有效列数 `32`
    - 输出有效行数 `16`
3. **数据格式**
    - 值使用 `32 位单精度浮点数`（`FP32`）
    - 索引使用 `U32`

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
