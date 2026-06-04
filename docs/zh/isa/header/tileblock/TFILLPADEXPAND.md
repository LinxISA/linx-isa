# TFILLPADEXPAND

## 说明

**数据块扩展填充（Tile Fill and Pad with Expand）**

`TFILLPADEXPAND` 将源 Tile 复制到目标 Tile 中，并允许目标 Tile 的行列尺寸大于源 Tile。有效区域外使用指定的填充值填充，扩展区域也使用相同填充值。

实现伪代码示意如下：
```pseudocode
// 扩展填充操作
for r in 0..(DstRow-1):                                // 遍历目标所有行
  for c in 0..(DstCol-1):                              // 遍历目标所有列
    if r < SrcValidRow && c < SrcValidCol:
      dst[r, c] = src[r, c]                              // 有效区域：复制源元素
    else:
      dst[r, c] = PadValue                               // 扩展/无效区域：填充值
```

---

## 汇编语法

```asm
TFILLPADEXPAND <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输出 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：目标 Tile 的总列数（必须）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：目标 Tile 的总行数，通过公式计算：`Row = DstTileSize / (Col × sizeof(DataType))`。
- **DataType**：输入/输出 Tile 元素的数据格式，支持类型见下表。
- **PadValue**：无效区域和扩展区域的填充值。本指令中 **必须**显式指定，可选：`Zero`、`Max`、`Min`（`Null` 不允许）。
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

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `TFILLPADEXPAND, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **尺寸扩展**：
    - `SrcTile::Row <= DstTile::Row`（目标行数可大于等于源行数）
    - `SrcTile::Col <= DstTile::Col`（目标列数可大于等于源列数）
- **有效边界**：`ValidRow <= SrcTile::Row`，`ValidCol <= SrcTile::Col`
- **数据类型**：`SrcTile::DataType == DstTile::DataType`
- **填充值**：`PadValue` 必须指定为 `Zero`、`Max` 或 `Min`，不允许 `Null`。
- **存储布局**：必须是行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TFILLPADEXPAND <LB0:16, LB1:8, LB2:32, FP32, zero>, T#1.reuse, ->T<2KB>
```

1. **操作内容**
    - 将 `T#1` Tile 的有效区域（8×16）复制到输出 Tile 并扩展，其余区域填充零
    - 输出：结果存入新的 `T` 队列 Tile 寄存器
2. **数据处理范围**
    - 有效列数 `16`（由 `LB0:16` 指定），总列数 `32`
    - 有效行数 `8`（由 `LB1:8` 指定），总行数由 `2KB / (32 × 4B) = 16` 行
3. **数据格式**
    - 使用 `32 位单精度浮点数`（`FP32`）格式
4. **扩展**
    - 输出 Tile 为 16×32，源仅 8×16，超出部分填充为零

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
