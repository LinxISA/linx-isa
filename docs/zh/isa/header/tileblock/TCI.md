# TCI

## 说明

**数据块连续整数生成（Tile Continuous Integer）**

`TCI` 从起始值开始生成连续整数序列（升序或降序），填充到输出 Tile 中。

实现伪代码示意如下：
```pseudocode
// 连续整数生成操作
for c in 0..(ValidCol-1):                              // 按列遍历
  if descending:
    dst[0, c] = start - c                                // 降序：start, start-1, start-2, ...
  else:
    dst[0, c] = start + c                                // 升序：start, start+1, start+2, ...
```

---

## 汇编语法

```asm
TCI <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, Dir>, [RegSrc], ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输出 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：输出 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：输出 Tile 的总行数，通过公式计算：`Row = DstTileSize / (Col × sizeof(DataType))`。
- **DataType**：输出 Tile 元素的数据格式，支持 `S32`、`U32`、`S16`、`U16`。
- **Dir**：生成方向，可选：`ASC`（升序）或 `DESC`（降序）。
- **RegSrc**：序列起始值，由 GGPR 提供（参见：[全局寄存器](../../register/common/ggpr.md)）。
- **DstTile**：输出 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输出。
- **Size**：输出 Tile 寄存器的空间大小（有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)）。

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TCI, DataType`
- [B.DATR](../../header/B.DATR.md) `Dir`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

## 约束条件

- **数据类型**：仅支持 `S32`、`U32`、`S16`、`U16`。
- **序列长度**：`ValidCol` 作为序列长度。
- **溢出行为**：当序列值超出数据类型的表示范围时，行为由硬件实现定义。
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **存储布局**：输出为行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TCI <LB0:64, LB1:1, U32, ASC>, [a0], ->T<256B>
```

1. **操作内容**
    - 从 `a0` 值开始生成升序连续整数序列
    - 输出：结果存入 `T` 队列 Tile 寄存器（1×64）
2. **数据处理范围**
    - 有效列数 `64`（序列长度）
    - 有效行数 `1`
3. **数据格式**
    - 使用 `32 位无符号整数`（`U32`）格式
4. **序列**
    - 输出：`[a0, a0+1, a0+2, ..., a0+63]`

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
