# TEXPANDS

## 说明

**数据块标量扩展(Tile Expand Scalar)**

`TEXPANDS` 将输入标量寄存器的内容广播/扩展到输出 Tile 的有效区域。 

实现伪代码示意如下：
```pseudocode
// 广播/扩展操作
for r in 0..(Rv-1):           // 遍历所有行
  for c in 0..(Cv-1):       // 遍历所有列
    dst[r, c] = scalar    // 标量广播/扩展
```

实现示意图如下：

![TEXPANDS](../../../figs/isa/tileop/TEXPANDS.png){ width="600" }

---

## 汇编语法

```asm
    TEXPANDS <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, [RegSrc], ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输出Tile中有效元素的列数。该参数可以通过以下3种形式配置到LB0寄存器中：
    - **reg**：通过全局寄存器[GGPR](../../register/common/ggpr.md)设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出Tile中有效元素的行数（可缺省，默认值：`1`）。该参数配置到LB1寄存器中，配置方式同上。
- **Col**：输出Tile的总列数（可缺省，默认值：等于`ValidCol`）。该参数配置到LB2寄存器中，配置方式同上。
- **Row**：输出Tile的总行数，通过公式计算：`Row = SrcTileSize / (Col × sizeof(DataType))`。
- **DataType**：输出Tile元素与标量的数据格式，支持类型见下表。
- **PadValue**：输出Tile无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。
- **RegSrc**：输入全局寄存器，用于存储标量值。（参见：[全局寄存器](../../register/common/ggpr.md)）
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

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TEXPANDS, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

## 约束条件

- **有效边界**：
    - `ValidRow <= Row`, `ValidCol <= Col`
- **存储布局**：
    - 必须是**行主序（RowMajor）**。
- **尺寸范围**：
    - Tile的行列/有效行列等参数大小均必须小于等于16bit。

---

## 汇编示例

```asm
    TEXPANDS <LB0:12, LB1:32, LB2:16, fp32, Zero>, [a1], ->T<1KB>
```

1. **操作内容**  
    - 输入：`a1` 全局寄存器
    - 输出：结果存入新的 `T` 队列Tile寄存器
2. **数据处理范围**  
    - 有效列数 `12`（由 `LB0:12` 指定）
    - 有效行数 `32`（由 `LB1:32` 指定）
    - 总列数 `16`（由 `LB2:16` 指定）
3. **数据格式**  
    - 使用 `16位浮点数`（`fp16`）格式处理数据  
    - 每个元素占2字节（影响内存布局计算）
4. **寄存器管理**   
    - 输出寄存器分配 `1KB` 空间（足够存储计算结果）
5. **特殊处理**  
    - 区域中**超出有效范围的部分**初始化为`Zero`（`PadValue::Zero`）  
    - 输出寄存器由硬件自动分配（`->T` 未指定具体寄存器号）

---

## 备注

此指令是TileOp模版块，软件只定义块头。
