# TCOLARGMAX

## 说明

**数据块列最大值索引（Tile Column ArgMax）**

`TCOLARGMAX` 对输入 Tile 的每一列所有行求最大值的位置索引（argmax），结果写入输出 Tile 中。可选同时输出每列最大值。

实现伪代码示意如下：
```pseudocode
// 列 argmax 归约操作
for c in 0..(Cv-1):                              // 遍历所有列
  max_idx = 0
  max_val = src[0, c]
  for r in 1..(Rv-1):                            // 遍历所有行
    if src[r, c] > max_val:
      max_val = src[r, c]
      max_idx = r
  dstIdx[0, c] = max_idx                          // 输出最大值行索引
  // 可选：dstVal[0, c] = max_val                 // 输出最大值
```

---

## 汇编语法

```asm
TCOLARGMAX <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, ->DstIdx<Size>, DstVal<Size>
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
- **DstIdx**：索引输出 Tile 寄存器（`S32`/`U32` 类型），每列输出最大值对应的行索引，支持 `T`/`U`/`M`/`N` 队列输出。
- **DstVal**：最大值输出 Tile 寄存器（可选，可缺省），输出每列最大值，类型与 `DataType` 一致。
- **Size**：输出 Tile 寄存器的空间大小（有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)）。

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TCOLARGMAX, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, ->DstIdx<Size>`
- [B.IOT](../../header/B.IOT.md) `last, ->DstVal<Size>`   （注：*可选*）

## 约束条件

- **输出形状**：
    - `DstIdx::ValidRow == DstIdx::Row == 1`，`DstIdx::ValidCol == ValidCol`
    - `DstVal`（若提供）：`DstVal::ValidRow == 1`，`DstVal::ValidCol == ValidCol`
- **数据类型**：
    - 源 Tile 数据类型仅支持浮点类型（`FP64`、`FP32`、`TF32`、`HF32`、`FP16`、`BF16`）。
    - `DstIdx` 元素类型为 `S32` 或 `U32`。
    - `DstVal`（若提供）元素类型与 `DataType` 一致。
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **存储布局**：输入 Tile 必须为行主序（RowMajor）；输出 Tile 为一行向量（行主序 RowMajor）。
- **索引行为**：当多个元素同为最大值时，返回最小行索引。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TCOLARGMAX <LB0:32, LB1:16, FP32>, T#1.reuse, ->U<128B>, T<128B>
```

1. **操作内容**
    - 输入：`T#1` Tile 寄存器（源数据）
    - 输出：索引结果存入 `U` 队列 Tile 寄存器；最大值结果存入 `T` 队列 Tile 寄存器
2. **数据处理范围**
    - 有效列数 `32`（由 `LB0:32` 指定）
    - 有效行数 `16`（由 `LB1:16` 指定）
3. **数据格式**
    - 使用 `32 位单精度浮点数`（`FP32`）格式处理数据
    - 索引输出为 `S32` 类型
4. **输出**
    - `U<128B>`：1 行 × 32 列 × 4 字节 = 128B 索引输出
    - `T<128B>`：1 行 × 32 列 × 4 字节 = 128B 最大值输出

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
