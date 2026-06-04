# TPOW

## 说明

**数据块逐元素幂运算（Tile Element-wise Power）**

`TPOW` 对两个输入 Tile 执行逐元素幂运算：以左源 Tile 为底数，右源 Tile 为指数，计算每个元素的幂，结果写入输出 Tile 中。

实现伪代码示意如下：
```pseudocode
// 逐元素幂运算操作
for r in 0..(Rv-1):                        // 遍历所有行
  for c in 0..(Cv-1):                      // 遍历所有列
    dst[r, c] = pow(srcBase[r, c], srcExp[r, c])  // 底数的指数次幂
```

---

## 汇编语法

```asm
TPOW <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcBase<.reuse>, SrcExp<.reuse>, ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输出 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：输出 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：输出 Tile 的总行数，通过公式计算：`Row = DstTileSize / (Col × sizeof(DataType))`。
- **DataType**：输入 Tile 元素的数据格式，支持类型见下表。
- **PadValue**：输出 Tile 无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。
- **SrcBase**：底数输入 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **SrcExp**：指数输入 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输入。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：输出 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输出。
- **Size**：输出 Tile 寄存器的空间大小（有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)）。

本指令支持数据类型（DataType）如下表所示：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | FP64 |
| b32 | FP32, TF32, HF32 |
| b16 | FP16, BF16 |

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TPOW, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcBase<.reuse>, SrcExp<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **参数一致性**：两个输入 Tile 的以下参数必须一致，否则硬件不保证结果正确性：
    - `SrcBase::Row == SrcExp::Row`，`SrcBase::Col == SrcExp::Col`
    - `SrcBase::ValidRow == SrcExp::ValidRow`，`SrcBase::ValidCol == SrcExp::ValidCol`
    - `SrcBase::DataType == SrcExp::DataType`
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **数据类型**：仅支持浮点类型（`FP64`、`FP32`、`TF32`、`HF32`、`FP16`、`BF16`）。
- **存储布局**：必须是行主序（RowMajor）。
- **定义域**：底数为零且指数为负数时，结果由硬件实现定义。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TPOW <LB0:16, LB1:32, FP32, zero>, T#1.reuse, M#2, ->T<1KB>
```

1. **操作内容**
    - 输入：`T#1` Tile 寄存器（底数），`M#2` Tile 寄存器（指数）
    - 输出：结果存入新的 `T` 队列 Tile 寄存器
2. **数据处理范围**
    - 有效列数 `16`（由 `LB0:16` 指定）
    - 有效行数 `32`（由 `LB1:32` 指定）
3. **数据格式**
    - 使用 `32 位单精度浮点数`（`FP32`）格式处理数据
4. **寄存器管理**
    - 输入寄存器 `T#1` 添加了 `.reuse` 标记，表示执行后保留该寄存器
    - `M#2` 未标记 `.reuse`，硬件可自动释放
    - 输出寄存器分配 `1KB` 空间
5. **特殊处理**
    - 区域中超出有效范围的部分初始化为零（`PadValue == zero`）

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
