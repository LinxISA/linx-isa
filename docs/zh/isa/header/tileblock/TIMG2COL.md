# TIMG2COL

## 说明

**数据块图像到列变换（Tile Image to Column）**

`TIMG2COL` 将卷积格式的输入 Tile 展开为矩阵乘友好的列格式（im2col 变换），用于类卷积工作负载的加速。变换将每个卷积窗口展平为一行，结果写入输出 Tile 中。

实现伪代码示意如下：
```pseudocode
// im2col 变换操作（由硬件实现定义具体行为）
for r in 0..(DstValidRow-1):                           // 遍历输出行（每个卷积窗口）
  for c in 0..(DstValidCol-1):                         // 遍历输出列（窗口内元素）
    dst[r, c] = im2col_map(src, r, c)                   // 根据卷积参数映射源元素
```

---

## 汇编语法

```asm
TIMG2COL <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, ->DstTile<Size>
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
- **SrcTile**：输入 Tile 寄存器（卷积格式），支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：输出 Tile 寄存器（列格式），支持 `T`/`U`/`M`/`N` 队列输出。
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

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `TIMG2COL, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **输入格式**：源 Tile 必须为卷积配置格式（卷积参数由硬件根据输入 Tile 的元数据隐式获取）。
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **数据类型**：`SrcTile::DataType == DstTile::DataType`
- **存储布局**：输出为行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TIMG2COL <LB0:64, LB1:128, FP16>, T#1.reuse, ->T<16KB>
```

1. **操作内容**
    - 将卷积格式的 `T#1` Tile 变换为列格式
    - 输出：结果存入新的 `T` 队列 Tile 寄存器
2. **数据处理范围**
    - 有效列数 `64`（由 `LB0:64` 指定）
    - 有效行数 `128`（由 `LB1:128` 指定）
3. **数据格式**
    - 使用 `16 位半精度浮点数`（`FP16`）格式

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
