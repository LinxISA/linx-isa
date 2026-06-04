# TCONCAT

## 说明

**数据块拼接（Tile Concatenate）**

`TCONCAT` 将两个源 Tile 沿列维度水平拼接，结果写入输出 Tile 中。输出 Tile 的有效列数等于两源有效列数之和，有效行数等于两源有效行数的最小值。

实现伪代码示意如下：
```pseudocode
// 水平拼接操作
for r in 0..(ValidRow-1):                              // 遍历有效行
  for c in 0..(DstValidCol-1):                         // 遍历目标所有列
    if c < Src0ValidCol:
      dst[r, c] = src0[r, c]                             // 左半部分：源 0 数据
    else:
      dst[r, c] = src1[r, c - Src0ValidCol]              // 右半部分：源 1 数据
```

---

## 汇编语法

```asm
TCONCAT <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile0<.reuse>, SrcTile1<.reuse>, ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输出 Tile（拼接后）的有效列数（= `Src0ValidCol + Src1ValidCol`）。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile（拼接后）的有效行数（可缺省，默认值：`min(Src0ValidRow, Src1ValidRow)`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：输出 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：输出 Tile 的总行数，通过公式计算：`Row = DstTileSize / (Col × sizeof(DataType))`。
- **DataType**：输入/输出 Tile 元素的数据格式，支持类型见下表。
- **PadValue**：输出 Tile 无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。
- **SrcTile0**：左侧输入 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **SrcTile1**：右侧输入 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输入。
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

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `TCONCAT, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **形状关系**：
    - `DstTile::ValidRow == min(SrcTile0::ValidRow, SrcTile1::ValidRow)`
    - `DstTile::ValidCol == SrcTile0::ValidCol + SrcTile1::ValidCol`
- **数据类型**：两个源 Tile 和输出 Tile 的元素类型必须一致。
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **行数不匹配**：若两个源 Tile 的行数不同，仅使用前 `min(Src0Row, Src1Row)` 行。
- **存储布局**：必须是行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TCONCAT <LB0:48, LB1:16, FP16>, T#1.reuse, U#2, ->T<1.5KB>
```

1. **操作内容**
    - 将 `T#1`（16×16）和 `U#2`（16×32）沿列方向水平拼接到输出 Tile
    - 输出：结果存入新的 `T` 队列 Tile 寄存器（16×48）
2. **数据处理范围**
    - 有效总列数 `48`（= 16 + 32，由 `LB0:48` 指定）
    - 有效行数 `16`（由 `LB1:16` 指定）
3. **数据格式**
    - 使用 `16 位半精度浮点数`（`FP16`）格式
4. **拼接**
    - 前 16 列来自 `T#1`，后 32 列来自 `U#2`

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
