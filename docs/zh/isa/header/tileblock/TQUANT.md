# TQUANT

## 说明

**数据块量化（Tile Quantization）**

`TQUANT` 将源 Tile 中的高精度数据（如 FP32）量化为低精度格式（如 FP8），同时生成指数、缩放因子和最大值等量化参数输出。

实现伪代码示意如下：
```pseudocode
// 量化操作
for r in 0..(ValidRow-1):                              // 遍历所有行
  // 计算每行量化参数
  row_max = max(abs(src[r, :]))                          // 行最大绝对值
  row_scale = ComputeScale(row_max, DstType)             // 计算缩放因子
  for c in 0..(ValidCol-1):                             // 遍历所有列
    dst[r, c] = Quantize(src[r, c], row_scale, DstType) // 量化元素
  // 可选输出
  dstExp[r, 0] = ComputeExponent(row_scale)              // 输出指数
  dstMax[r, 0] = row_max                                 // 输出最大值
  dstScale[r, 0] = row_scale                             // 输出缩放因子
```

---

## 汇编语法

```asm
TQUANT <LB0:ValidCol, LB1:ValidRow, LB2:Col, SrcType, DstType>, SrcTile<.reuse>, ->DstTile<Size>, DstExp<Size>, DstMax<Size>, DstScale<Size>
```

## 汇编符号

- **ValidCol**：输出 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：输出 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：输出 Tile 的总行数，通过公式计算：`Row = DstTileSize / (Col × sizeof(SrcType))`。
- **SrcType**：源数据类型，支持 `FP32`、`FP16`、`BF16`。
- **DstType**：目标（量化后）数据类型，支持 `FP8(E4M3)`、`FP8(E5M2)`、`INT8`、`INT4` 等低精度格式。
- **SrcTile**：输入 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：量化后的输出 Tile 寄存器，元素类型为 `DstType`。
- **DstExp**：指数输出 Tile（可选），每行一个指数值。
- **DstMax**：最大值输出 Tile（可选），每行一个最大值。
- **DstScale**：缩放因子输出 Tile（可选），每行一个缩放因子。
- **Size**：输出 Tile 寄存器的空间大小（有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)）。

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TQUANT, SrcType, DstType`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, ->DstTile<Size>`
- [B.IOT](../../header/B.IOT.md) `->DstExp<Size>`    （注：*可选*）
- [B.IOT](../../header/B.IOT.md) `->DstMax<Size>`    （注：*可选*）
- [B.IOT](../../header/B.IOT.md) `last, ->DstScale<Size>`   （注：*可选*）

## 约束条件

- **量化方式**：支持逐行（per-row）或逐张量（per-tensor，ValidRow=1）量化。
- **输出参数**：
    - `DstExp`（若提供）：每行一个指数值，`S32` 类型。
    - `DstMax`（若提供）：每行一个最大值，与 `SrcType` 相同。
    - `DstScale`（若提供）：每行一个缩放因子，与 `SrcType` 相同。
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **存储布局**：输入/输出为行主序（RowMajor）；参数输出为一维列向量（列主序 ColMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TQUANT <LB0:64, LB1:32, FP32, E4M3>, T#1.reuse, ->U<512B>, M<128B>, N<128B>
```

1. **操作内容**
    - 将 `T#1` Tile（32×64 FP32）量化为 E4M3 格式
    - 输出量化指数和最大值参数
2. **数据处理范围**
    - 有效列数 `64`
    - 有效行数 `32`
3. **量化**
    - `U<512B>`：量化后数据（32×64×1B = 2KB...此处 Size 匹配 32×64 E4M3 = 512B）
    - `M<128B>`：指数输出（32 行 × 4B = 128B，S32）
    - `N<128B>`：最大值输出（32 行 × 4B = 128B，FP32）

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
