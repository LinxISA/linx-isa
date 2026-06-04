# TPARTMUL

## 说明

**数据块部分逐元素乘法（Tile Partial Element-wise Multiplication）**

`TPARTMUL` 在目标 Tile 的有效区域内对两个源 Tile 执行逐元素乘法。两个源 Tile 的有效区域可能不完全重叠：重叠处求积，仅单侧有效处传播该侧的值，均无效处由实现定义。

实现伪代码示意如下：
```pseudocode
// 部分逐元素乘法操作
for r in 0..(ValidRow-1):
  for c in 0..(ValidCol-1):
    s0_valid = r < src0.ValidRow && c < src0.ValidCol
    s1_valid = r < src1.ValidRow && c < src1.ValidCol
    if s0_valid && s1_valid:
      dst[r, c] = src0[r, c] * src1[r, c]
    else if s0_valid:
      dst[r, c] = src0[r, c]
    else if s1_valid:
      dst[r, c] = src1[r, c]
```

---

## 汇编语法

```asm
TPARTMUL <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile0<.reuse>, SrcTile1<.reuse>, ->DstTile<Size>
```

## 汇编符号

- **ValidCol**、**ValidRow**：目标 Tile 有效列数/行数，配置方式同 `TPARTADD`。
- **Col**：目标 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。
- **Row**：目标 Tile 的总行数，`Row = DstTileSize / (Col × sizeof(DataType))`。
- **DataType**：输入/输出 Tile 元素的数据格式，支持类型同 `TPARTADD`。
- **PadValue**：无效区域的填充值（可缺省，默认值：`Null`）。
- **SrcTile0**、**SrcTile1**：输入 Tile 寄存器。
- **reuse**（后缀）：指示当前指令提交后保留寄存器。
- **DstTile**：输出 Tile 寄存器。
- **Size**：输出 Tile 寄存器的空间大小。

---

## 编码格式

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TPARTMUL, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, last, ->DstTile<Size>`

## 约束条件

与 `TPARTADD` 相同，详见 [TPARTADD](./TPARTADD.md) 约束条件章节。

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
