# TMRGSORT

## 说明

**数据块归并排序（Tile Merge Sort）**

`TMRGSORT` 对单个输入 Tile 中的多个已排序分段执行归并排序：将源 Tile 按 `BlockLen` 等分为若干段（段内已有序），归并各段到输出 Tile 中。

对于多列表归并（多个独立已排序 Tile 的归并），请使用 [TMRGSORT4](TMRGSORT4.md)。

实现伪代码示意如下：
```pseudocode
// 单列表多段归并
for r in 0..(ValidRow-1):
  // 将 src 每行按 blockLen 分为若干段，段内已有序
  // 归并各段到 dst
  dst[r, :] = KWayMerge([src[r, k*blockLen..(k+1)*blockLen-1] for k in 0..(ValidCol/blockLen)-1])
```

---

## 汇编语法

```asm
TMRGSORT <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, BlockLen>, SrcTile<.reuse>, ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输出 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：输出 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **DataType**：输入/输出 Tile 元素的数据格式，支持 `FP32`、`FP16`。
- **BlockLen**：每个已排序分段的长度，必须为 64 的倍数。编码到 [B.DATR](../../header/B.DATR.md) 中。
- **SrcTile**：输入 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：输出 Tile 寄存器，归并后的有序结果。支持 `T`/`U`/`M`/`N` 队列输出。
- **Size**：输出 Tile 寄存器的空间大小（有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)）。

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TMRGSORT, DataType`
- [B.DATR](../../header/B.DATR.md) `BlockLen`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`

## 约束条件

- `ValidCol` 必须为 `blockLen × N` 的倍数（N 为分段数）。
- 重复次数 `repeatTimes = ValidCol / (blockLen × N)` 必须在 `[1, 255]` 范围内。
- `blockLen` 必须为 64 的倍数。
- **数据类型**：仅支持 `FP32`、`FP16`。
- **存储布局**：必须是行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TMRGSORT <LB0:256, LB1:4, LB2:256, FP16, 64>, T#1.reuse, ->T<2KB>
```

1. **操作内容**
    - 将 `T#1` Tile 的每行 256 个元素（= 4 段 × 64 元素）归并排序
    - 输出：结果存入 `T` 队列 Tile 寄存器
2. **单列表归并**
    - `blockLen=64`：每段 64 个已排序元素，共 4 段

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
