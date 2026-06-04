# TTRI

## 说明

**数据块三角掩码生成（Tile Triangular Mask）**

`TTRI` 生成三角（下三角或上三角）掩码 Tile，用于 Attention 机制等场景中掩码操作。掩码值为 `1` 表示保留，`0` 表示遮蔽。

实现伪代码示意如下：
```pseudocode
// 三角掩码生成操作
for r in 0..(ValidRow-1):                              // 遍历所有行
  for c in 0..(ValidCol-1):                            // 遍历所有列
    if is_upper:                                         // 上三角
      dst[r, c] = (c >= r + diagonal) ? 1 : 0
    else:                                                // 下三角
      dst[r, c] = (c <= r + diagonal) ? 1 : 0
```

---

## 汇编语法

```asm
TTRI <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, TriMode>, [RegDiag], ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输出 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：输出 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：输出 Tile 的总行数，通过公式计算：`Row = DstTileSize / (Col × sizeof(DataType))`。
- **DataType**：输出 Tile 元素的数据格式，支持 `S32`、`U32`、`S16`、`U16`、`FP32`、`FP16`、`BF16`。
- **TriMode**：三角模式，可选：`LOWER`（下三角）或 `UPPER`（上三角）。
- **RegDiag**：对角线偏移量，由 GGPR 提供。正值为超对角线/子对角线偏移，负值为反向。
- **DstTile**：输出 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输出。
- **Size**：输出 Tile 寄存器的空间大小（有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **PadValue**：输出 Tile 无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。编码到 [B.DATR](../../header/B.DATR.md) 中。

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TTRI, DataType`
- [B.DATR](../../header/B.DATR.md) `TriMode`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegDiag`

## 约束条件

- **对角线偏移**：`diagonal` 为有符号整数，默认值为 `0`（主对角线）。
    - 下三角 + `diagonal=0`：主对角线及以下为 `1`。
    - 上三角 + `diagonal=0`：主对角线及以上为 `1`。
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **存储布局**：输出为行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TTRI <LB0:16, LB1:16, U16, LOWER>, [a0], ->T<512B>
```

1. **操作内容**
    - 生成 16×16 的下三角掩码（含对角线），偏移量由 `a0` 指定
    - 输出：结果存入 `T` 队列 Tile 寄存器
2. **数据处理范围**
    - 有效列数 `16`
    - 有效行数 `16`
3. **掩码**
    - `a0=0`：主对角线及以下为 1，以上为 0
    - `a0=-1`：主对角线以下一行开始为 1（不含主对角线）

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
