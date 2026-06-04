# TMRGSORT4

## 说明

**数据块多列表归并排序（Tile Merge Sort — 4 Lists）**

`TMRGSORT4` 对 4 个已排序的输入 Tile 执行多列表归并排序：从每个源 Tile 读取对应行的有序数据，按值归并后写入输出 Tile 中，并通过 GGPR 寄存器输出实际参与归并的列表数量。

单列表多段归并请使用 [TMRGSORT](TMRGSORT.md)。

实现伪代码示意如下：
```pseudocode
// 多列表归并
for r in 0..(ValidRow-1):
  // 将 4 个已排序列表归并
  dst[r, :] = Merge([src0[r,:], src1[r,:], src2[r,:], src3[r,:]])
// 输出实际生效的列表数
exeNum = CountActiveLists(src0, src1, src2, src3)
```

---

## 汇编语法

```asm
TMRGSORT4 <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, SrcTile3<.reuse>, ->DstTile<Size>, [RegDst]
```

## 汇编符号

- **ValidCol**：输出 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：输出 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **DataType**：输入/输出 Tile 元素的数据格式，支持 `FP32`、`FP16`。
- **SrcTile0~3**：4 个已排序输入 Tile 寄存器。每个源 Tile 的 `DataType` 和 `ValidRow` 必须一致。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **RegDst**：输出 GGPR 寄存器（可选，64-bit），硬件写入各源列表的实际归并状态。寄存器内分为 4 段 16-bit 数据：`bit[15:0]` 对应 SrcTile0，`bit[31:16]` 对应 SrcTile1，`bit[47:32]` 对应 SrcTile2，`bit[63:48]` 对应 SrcTile3。每段值为 `1` 表示该列表参与了归并，`0` 表示未参与。
- **DstTile**：输出 Tile 寄存器，归并后的有序结果。支持 `T`/`U`/`M`/`N` 队列输出。
- **Size**：输出 Tile 寄存器的空间大小（有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **PadValue**：输出 Tile 无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。编码到 [B.DATR](../../header/B.DATR.md) 中。

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TMRGSORT4, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>`
- [B.IOT](../../header/B.IOT.md) `SrcTile2<.reuse>, SrcTile3<.reuse>, last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegDst`   （注：*可选*）

## 约束条件

- 4 个源 Tile 的 `DataType` 和 `ValidRow` 必须一致。
- 每个源 Tile 内部已按值有序。
- **数据类型**：仅支持 `FP32`、`FP16`。
- **存储布局**：必须是行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
