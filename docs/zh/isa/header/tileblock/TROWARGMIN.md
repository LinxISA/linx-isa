# TROWARGMIN

## 说明

**数据块行最小值索引（Tile Row ArgMin）**

`TROWARGMIN` 对输入 Tile 的每一行所有列求最小值的位置索引（argmin），结果写入输出 Tile 中。可选同时输出每行最小值。

实现伪代码示意如下：
```pseudocode
// 行 argmin 归约操作
for r in 0..(Rv-1):                              // 遍历所有行
  min_idx = 0
  min_val = src[r, 0]
  for c in 1..(Cv-1):                            // 遍历所有列
    if src[r, c] < min_val:
      min_val = src[r, c]
      min_idx = c
  dstIdx[r, 0] = min_idx                          // 输出最小值列索引
  // 可选：dstVal[r, 0] = min_val                 // 输出最小值
```

---

## 汇编语法

```asm
TROWARGMIN <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, ->DstIdx<Size>, DstVal<Size>
```

## 汇编符号

- **ValidCol**：输出 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：输出 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：输出 Tile 的总行数，通过公式计算：`Row = DstTileSize / (Col × sizeof(DataType))`。
- **DataType**：输入 Tile 元素的数据格式，支持 `FP64`、`FP32`、`TF32`、`HF32`、`FP16`、`BF16`。
- **PadValue**：输出 Tile 无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。
- **SrcTile**：输入 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstIdx**：索引输出 Tile 寄存器（`S32`/`U32` 类型），每行输出最小值对应的列索引，支持 `T`/`U`/`M`/`N` 队列输出。
- **DstVal**：最小值输出 Tile 寄存器（可选，可缺省），输出每行最小值，类型与 `DataType` 一致。
- **Size**：输出 Tile 寄存器的空间大小（有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)）。

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TROWARGMIN, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, ->DstIdx<Size>`
- [B.IOT](../../header/B.IOT.md) `last, ->DstVal<Size>`   （注：*可选*）

## 约束条件

- **输出形状**：
    - `DstIdx::ValidCol == DstIdx::Col == 1`，`DstIdx::ValidRow == ValidRow`
    - `DstVal`（若提供）：`DstVal::ValidCol == 1`，`DstVal::ValidRow == ValidRow`
- **数据类型**：
    - 源 Tile 数据类型仅支持浮点类型（`FP64`、`FP32`、`TF32`、`HF32`、`FP16`、`BF16`）。
    - `DstIdx` 元素类型为 `S32` 或 `U32`。
    - `DstVal`（若提供）元素类型与 `DataType` 一致。
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **存储布局**：输入 Tile 必须为行主序（RowMajor）；输出 Tile 为一维列向量（列主序 ColMajor）。
- **索引行为**：当多个元素同为最小值时，返回最小列索引。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TROWARGMIN <LB0:64, LB1:8, FP16>, T#3.reuse, ->T<16B>
```

1. **操作内容**
    - 输入：`T#3` Tile 寄存器（源数据）
    - 输出：索引结果存入 `T` 队列 Tile 寄存器（8 行 × 1 列 = 8 个索引值）
2. **数据处理范围**
    - 有效列数 `64`（由 `LB0:64` 指定）
    - 有效行数 `8`（由 `LB1:8` 指定）
3. **数据格式**
    - 使用 `16 位半精度浮点数`（`FP16`）格式处理数据
    - 索引输出为 `S32` 类型
4. **输出**
    - `T<16B>`：8 行 × 1 列 × 2 字节 = 16B 索引输出（此处仅为索引，不输出最小值）

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
