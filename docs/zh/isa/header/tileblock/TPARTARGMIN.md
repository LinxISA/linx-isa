# TPARTARGMIN

## 说明

**数据块部分逐元素最小值与索引选择（Tile Partial Element-wise ArgMin）**

`TPARTARGMIN` 在目标 Tile 的有效区域内对两个源 Tile 执行逐元素最小值选择，同时返回胜出元素的来源索引。重叠处较小值及其索引胜出；仅单侧有效处传播其值和索引；均无效处由实现定义。

实现伪代码示意如下：
```pseudocode
// 部分逐元素 argmin 操作
for r in 0..(ValidRow-1):
  for c in 0..(ValidCol-1):
    s0_valid = r < src0.ValidRow && c < src0.ValidCol
    s1_valid = r < src1.ValidRow && c < src1.ValidCol
    if s0_valid && s1_valid:
      if src0Val[r,c] < src1Val[r,c]:
        dstVal[r,c] = src0Val[r,c]; dstIdx[r,c] = src0Idx[r,c]
      else:
        dstVal[r,c] = src1Val[r,c]; dstIdx[r,c] = src1Idx[r,c]
    else if s0_valid:
      dstVal[r,c] = src0Val[r,c]; dstIdx[r,c] = src0Idx[r,c]
    else if s1_valid:
      dstVal[r,c] = src1Val[r,c]; dstIdx[r,c] = src1Idx[r,c]
```

---

## 汇编语法

```asm
TPARTARGMIN <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcVal0<.reuse>, SrcVal1<.reuse>, SrcIdx0<.reuse>, SrcIdx1<.reuse>, ->DstVal<Size>, DstIdx<Size>
```

## 汇编符号

- **ValidCol**、**ValidRow**：目标 Tile 有效列数/行数，配置方式同 `TPARTADD`。
- **Col**：目标 Tile 的总列数（可缺省，默认值：等于 `ValidCol`），配置方式同 `TPARTADD`。
- **DataType**：值 Tile 元素的数据格式，支持类型见下表。
- **SrcVal0**、**SrcVal1**：两个源值 Tile 寄存器。
- **SrcIdx0**、**SrcIdx1**：两个源索引 Tile 寄存器（`S16`/`U16` 或 `S32`/`U32`）。
- **reuse**（后缀）：指示当前指令提交后保留寄存器。
- **DstVal**：胜出值输出 Tile 寄存器，类型与 `DataType` 一致。
- **DstIdx**：胜出索引输出 Tile 寄存器，类型与 `SrcIdx` 一致。
- **Size**：输出 Tile 寄存器的空间大小。
- **PadValue**：输出 Tile 无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。编码到 [B.DATR](../../header/B.DATR.md) 中。

本指令支持的值数据类型：

| 数据位宽 | 值类型 | 索引类型 |
|----------|--------|----------|
| b32 | FP32 | S32, U32 |
| b16 | FP16, BF16 | S16, U16 |

---

## 编码格式

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TPARTARGMIN, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcVal0<.reuse>, SrcVal1<.reuse>, ->DstVal<Size>`
- [B.IOT](../../header/B.IOT.md) `SrcIdx0<.reuse>, SrcIdx1<.reuse>, last, ->DstIdx<Size>`

## 约束条件

- **胜出逻辑**：`src0Val < src1Val` 时 src0 胜出；`src1Val <= src0Val` 时 src1 胜出。
- **有效区域语义**：重叠处比较并选择；单侧有效处直接传播该侧值-索引对。
- **索引类型一致性**：`SrcIdx0::DataType == SrcIdx1::DataType == DstIdx::DataType`
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **存储布局**：必须是行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
