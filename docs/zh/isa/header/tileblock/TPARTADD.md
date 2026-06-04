# TPARTADD

## 说明

**数据块部分逐元素加法（Tile Partial Element-wise Addition）**

`TPARTADD` 在目标 Tile 的有效区域内对两个源 Tile 执行逐元素加法。两个源 Tile 的有效区域可能不完全重叠：重叠处求和，仅单侧有效处传播该侧的值，均无效处由实现定义。

实现伪代码示意如下：
```pseudocode
// 部分逐元素加法操作
for r in 0..(ValidRow-1):                              // 遍历所有行
  for c in 0..(ValidCol-1):                            // 遍历所有列
    s0_valid = r < src0.ValidRow && c < src0.ValidCol
    s1_valid = r < src1.ValidRow && c < src1.ValidCol
    if s0_valid && s1_valid:
      dst[r, c] = src0[r, c] + src1[r, c]                // 重叠：求和
    else if s0_valid:
      dst[r, c] = src0[r, c]                              // 仅 src0 有效：传播
    else if s1_valid:
      dst[r, c] = src1[r, c]                              // 仅 src1 有效：传播
    // else: 实现定义
```

---

## 汇编语法

```asm
TPARTADD <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile0<.reuse>, SrcTile1<.reuse>, ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：目标 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：目标 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：目标 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：目标 Tile 的总行数，通过公式计算：`Row = DstTileSize / (Col × sizeof(DataType))`。
- **DataType**：输入/输出 Tile 元素的数据格式，支持类型见下表。
- **PadValue**：输出 Tile 无效区域的填充值（可缺省，默认值：`Null`）。
- **SrcTile0**、**SrcTile1**：输入 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **reuse**（后缀）：指示当前指令提交后保留寄存器。
- **DstTile**：输出 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输出。
- **Size**：输出 Tile 寄存器的空间大小。

本指令支持数据类型（DataType）如下表所示：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | S64, U64, FP64 |
| b32 | S32, U32, FP32, TF32, HF32 |
| b16 | S16, U16, FP16, BF16 |
| b8  | S8,  U8,  FP8(E4M3, E5M2) |

---

## 编码格式

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TPARTADD, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **有效区域语义**：重叠区域执行逐元素操作；单侧有效区域传播该侧值；均无效区域行为由硬件实现定义。
- **数据类型一致性**：`SrcTile0::DataType == SrcTile1::DataType == DstTile::DataType`
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **存储布局**：必须是行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
