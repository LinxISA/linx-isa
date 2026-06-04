# TSORT32

## 说明

**数据块 32 元素块排序（Tile Sort 32-element Blocks）**

`TSORT32` 对源 Tile 的每个 32 元素块与对应的索引 Tile 一起排序，将排序后的值-索引对写入输出 Tile 中。

实现伪代码示意如下：
```pseudocode
// 32 元素块排序操作
for block in 0..(NumBlocks-1):                         // 遍历每个 32 元素块
  pairs = [(src_val[block*32+k], src_idx[block*32+k]) for k in 0..31]
  sorted_pairs = SortByValue(pairs)                      // 按值降序排序
  for k in 0..31:
    dst[block*32+k] = sorted_pairs[k]                    // 写入排序后的值-索引对
```

---

## 汇编语法

```asm
TSORT32 <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, SrcIdxTile<.reuse>, ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输出 Tile 中有效元素的列数（必须为 32 的倍数）。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **DataType**：输入/输出 Tile 元素的数据格式，支持 `FP32`、`FP16`、`BF16`。
- **SrcTile**：值输入 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **SrcIdxTile**：索引输入 Tile 寄存器（类型 `U32`），支持 `T`/`U`/`M`/`N` 队列输入。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：输出 Tile 寄存器，按排序后的值-索引交错存储。支持 `T`/`U`/`M`/`N` 队列输出。
- **Size**：输出 Tile 寄存器的空间大小（有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **PadValue**：输出 Tile 无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。编码到 [B.DATR](../../header/B.DATR.md) 中。

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TSORT32, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, SrcIdxTile<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **列约束**：`ValidCol` 必须为 32 的倍数，每 32 个元素作为一个独立排序块。
- **数据类型**：`SrcTile::DataType` 仅支持 `FP32`、`FP16`、`BF16`；`SrcIdxTile` 为 `U32` 类型。
- **排序方式**：按值降序排序。若值相同，索引较小的元素优先。
- **输出格式**：输出 Tile 按 [value, index] 对交错排列，元素数量为输入的 2 倍。
- **存储布局**：必须是行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TSORT32 <LB0:64, LB1:1, LB2:64, FP16>, T#1.reuse, U#2, ->T<512B>
```

1. **操作内容**
    - 对 `T#1` Tile 的 2 个 32 元素块（64 ÷ 32 = 2）分别排序
    - 索引由 `U#2` 提供
    - 输出：排序后的值-索引对存入 `T` 队列 Tile 寄存器
2. **数据处理范围**
    - 有效列数 `64`（= 2 个 32 元素块）
    - 有效行数 `1`
3. **数据格式**
    - 值使用 `16 位半精度浮点数`（`FP16`）
    - 索引使用 `U32`

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
