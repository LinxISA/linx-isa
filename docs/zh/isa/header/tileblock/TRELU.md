# TRELU

## 说明

`TRELU` 对输入 Tile 逐元素ReLu，结果写入输出 Tile 中。 

实现伪代码示意如下：
```pseudocode
// 逐元素ReLu
for r in 0..(Rv-1):           // 遍历所有行
  for c in 0..(Cv-1):       // 遍历所有列
    dst[r, c] = (src[r, c] > 0) ? src[r, c] : 0    // 对应位置元素ReLu
```

实现示意图如下：

![TRELU](../../../figs/isa/tileop/TRELU.png){ width="800" }

---

## 汇编语法

```asm
    TRELU <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输入Tile中有效元素的列数。该参数可以通过以下3种形式配置到LB0寄存器中：
    - **reg**：通过全局寄存器[GGPR](../../register/common/ggpr.md)设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输入Tile中有效元素的行数（可缺省，默认值：`1`）。该参数配置到LB1寄存器中，配置方式同上。
- **Col**：输入Tile的总列数（可缺省，默认值：等于`ValidCol`）。该参数配置到LB2寄存器中，配置方式同上。
- **Row**：输入Tile的总行数，通过公式计算：`Row = SrcTileSize / (Col × sizeof(DataType))`。
- **DataType**：输入Tile元素的数据格式，支持类型见下表。
- **PadValue**：输出Tile无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。
- **SrcTile**：输入Tile寄存器，支持`T`/`U`/`M`/`N`队列输入（参见：[Tile寄存器](../../register/common/tilereg.md)）。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：输出Tile寄存器，支持`T`/`U`/`M`/`N`队列输出。
- **Size**：输出Tile寄存器的空间大小（有效范围参见：[Tile寄存器](../../register/common/tilereg.md)）。

本指令支持数据类型（DataType）如下表所示：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | S64, U64, FP64 |
| b32 | S32, U32, FP32, TF32, HF32 |
| b16 | S16, U16, FP16, BF16 |
| b8  | S8,  U8,  FP8(E4M3, E5M2) |

---

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TRELU, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`    （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`    （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`    （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **尺寸范围**：
    - 输入Tile的行列/有效行列等参数大小均必须小于等于16bit。
    - 有效边界：`ValidRow <= Row`, `ValidCol <= Col`
- **数据布局**：必须是行主序（RowMajor）。
- **特殊输入**：当输入为负数/NaN时，行为由目标定义。

---

## 汇编示例

```asm
    TRELU <LB0:30, LB1:16, LB2:32, u16>, U#1.reuse, ->T<1KB>
```

1. **操作内容**  
    - 输入：`U#1` Tile寄存器
    - 输出：结果存入新的 `T` 队列Tile寄存器
2. **数据处理范围**  
    - 只处理前 `30列`（由 `LB0:30` 指定），总列数为：`32`（`LB2:32`）
    - 有效行数为 `16`（`LB1:16`）  
3. **数据格式**  
    - 使用 `16位整数`（`u16`）格式处理数据  
    - 每个元素占2字节（影响内存布局计算）
4. **寄存器管理**  
    - 输入寄存器 `U#1 添加了 `.reuse` 标记，表示**执行后保留该寄存器**  
    - 输出寄存器分配 `1KB` 空间（足够存储计算结果）
5. **特殊处理**  
    - 区域中**超出有效范围的部分**不初始化（`PadValue` 缺省）  
    - 输出寄存器由硬件自动分配（`->T` 未指定具体寄存器号）

---

## ReLU操作

ReLU（Rectified Linear Unit）是一种广泛使用的激活函数，尤其在深度学习和神经网络中。它的核心行为是：保留正输入值，将负输入值置零。

特点：

- **非线性**：虽然ReLU在正区间是线性的，但由于在负区间截断为零，整体是非线性的。这使得神经网络能够学习复杂的非线性关系。
- **计算简单**：只涉及比较和取最大值操作，计算效率高（相比sigmoid、tanh等函数）。
- **稀疏性**：当输入为负时输出为零，可以产生稀疏的激活，有助于减少参数依赖和过拟合。
- **梯度特性**：
    - 在正区间梯度恒为1，避免了梯度消失问题（尤其在深层网络中）。
    - 在负区间梯度为0，可能导致“神经元死亡”（Dead Neurons）问题：一旦某个神经元输出为0（比如权重更新后大部分输入都落入负区间），它将永远输出0，梯度也为0，无法再更新。

为了解决 “神经元死亡” 问题，同时支持一些ReLU的变种：

- Leaky ReLU：允许负区间有一个小的斜率（如0.01），即当 x < 0 时输出 0.01x。（参见[TLRELU](./TLRELU.md)）
- Parametric ReLU：将负区间的斜率作为可学习的参数。（参见[TPRELU](./TPRELU.md)）

## 备注

此指令是TileOp模版块，软件只定义块头。
