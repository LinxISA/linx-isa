# TSHRS

## 说明

**数据块按标量右移(Tile Shift-Right by Scalar)**

`TSHRS` 将输入 Tile 逐元素右移 标量 指示的位数，结果写入输出 Tile 中。 

实现伪代码示意如下：
```pseudocode
// 逐元素右移操作
for r in 0..(Rv-1):           // 遍历所有行
  for c in 0..(Cv-1):       // 遍历所有列
    dst[r, c] = src[r, c] >> scalar  // 逐元素右移标量位数
```

实现示意图如下：

![TSHRS](../../../figs/isa/tileop/TSHRS.png){ width="800" }

---

## 汇编语法

```asm
    TSHRS <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, [RegSrc], ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输入Tile中有效元素的列数。该参数可以通过以下3种形式配置到LB0寄存器中：
    - **reg**：通过全局寄存器[GGPR](../../register/common/ggpr.md)设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输入Tile中有效元素的行数（可缺省，默认值：`1`）。该参数配置到LB1寄存器中，配置方式同上。
- **Col**：输入Tile的总列数（可缺省，默认值：等于`ValidCol`）。该参数配置到LB2寄存器中，配置方式同上。
- **Row**：输入Tile的总行数，通过公式计算：`Row = SrcTileSize / (Col × sizeof(DataType))`。
- **DataType**：输入Tile元素与标量的数据格式，支持类型见下表。
- **PadValue**：输出Tile无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。
- **SrcTile**：输入Tile寄存器，支持`T`/`U`/`M`/`N`队列输入（参见：[Tile寄存器](../../register/common/tilereg.md)）。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **RegSrc**：输入全局寄存器，用于存储标量值。（参见：[全局寄存器](../../register/common/ggpr.md)）
- **DstTile**：输出Tile寄存器，支持`T`/`U`/`M`/`N`队列输出。
- **Size**：输出Tile寄存器的空间大小（有效范围参见：[Tile寄存器](../../register/common/tilereg.md)）。

本指令支持数据类型（DataType）如下表所示：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | S64, U64 |
| b32 | S32, U32 |
| b16 | S16, U16 |
| b8  | S8,  U8  |

---

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TSHRS, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

## 约束条件

- **静态参数**：
    - `SrcTile::Row == DstTile::Row`
    - `SrcTile::Col == DstTile::Col`
- **动态参数**：
    - `SrcTile::ValidRow == DstTile::ValidRow`
    - `SrcTile::ValidCol == DstTile::ValidCol`
- **有效边界**：
    - `ValidRow <= Row`, `ValidCol <= Col`
- **数据类型**：
    - `SrcTile::DataType == DstTile::DataType`
- **存储布局**：
    - 必须是**行主序（RowMajor）**。
- **尺寸范围**：
    - Tile的行列/有效行列等参数大小均必须小于等于16bit。

---

## 汇编示例

```asm
    TSHRS <LB0:16, LB1:32, u16>, T#3.reuse, [a1], ->T<1KB>
```

1. **操作内容**  
    - 输入：`T#3` Tile寄存器；`a1` 全局寄存器
    - 输出：结果存入新的 `T` 队列Tile寄存器
2. **数据处理范围**  
    - 有效列数 `16`（由 `LB0:16` 指定）  
    - 有效行数 `32`（由 `LB1:32` 指定）  
    - 总列数缺省，默认等于 `16`
3. **数据格式**  
    - 使用 `16位整数`（`u16`）格式处理数据  
    - 每个元素占1字节（影响内存布局计算）
4. **寄存器管理**  
    - 输入寄存器 `T#3` 添加了 `.reuse` 标记，表示**执行后保留该寄存器**  
    - 输出寄存器分配 `1KB` 空间（足够存储计算结果）
5. **特殊处理**  
    - 区域中**超出有效范围的部分**不初始化（`PadValue` 缺省）  
    - 输出寄存器由硬件自动分配（`->T` 未指定具体寄存器号）

---

## 备注

此指令是TileOp模版块，软件只定义块头。
