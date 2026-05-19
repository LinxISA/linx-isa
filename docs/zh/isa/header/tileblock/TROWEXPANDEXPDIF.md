# TROWEXPANDEXPDIF

## 说明

**数据块行广播指数差(Tile Row Expand with Exponent Different)**

`TROWEXPANDEXPDIF` 用第一个输入 Tile 每一行逐元素与第二个输入 Tile 对应行第一个元素计算指数差，结果写入输出 Tile 中。 

实现伪代码示意如下：
```pseudocode
// 行广播指数差操作
for r in 0..(Rv-1):       // 遍历所有行
  for c in 0..(Cv-1):     // 遍历所有列
    dst[r, c] = exp(src0[r, c] - src1[r, 0])    // 逐元素指数差
```

实现示意图如下：

![TROWEXPANDADD](../../../figs/isa/tileop/TROWEXPANDADD.png){ width="900" }

---

## 汇编语法

```asm
    TROWEXPANDEXPDIF <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile0<.reuse>, SrcTile1<.reuse>, ->DstTile<Size>
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
- **SrcTile0/1**：输入Tile寄存器，支持`T`/`U`/`M`/`N`队列输入（参见：[Tile寄存器](../../register/common/tilereg.md)）。
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

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TROWEXPANDEXPDIF, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **动态参数**：
    - `SrcTile0::ValidRow == SrcTile1::ValidRow == DstTile::ValidRow`
    - `SrcTile0::ValidCol == DstTile::ValidCol`
    - `SrcTile1::ValidCol == SrcTile1::Col == 1`
- **有效边界**：
    - `ValidRow <= Row`, `ValidCol <= Col`
- **数据类型**：
    - `SrcTile0::DataType == SrcTile1::DataType == DstTile::DataType`
- **存储布局**：
    - 输入输出 Tile 必须是**行主序（RowMajor）**；
- **尺寸范围**：
    - Tile的行列/有效行列等参数大小均必须小于等于16bit。

---

## 汇编示例

```asm
    TROWEXPANDEXPDIF <LB0:16, LB1:24, fp16>, T#1, T#4.reuse, ->T<512B>
```

1. **操作内容**  
    - 输入：`T#1` 和 `T#4` Tile寄存器
    - 输出：结果存入新的 `T` 队列Tile寄存器
2. **数据处理范围**  
    - 有效列数 `16`（由 `LB0:16` 指定）  
    - 有效行数 `24`（由 `LB1:24` 指定）  
    - 总列数缺省，默认等于 `16`
3. **数据格式**  
    - 使用 `16位浮点数`（`fp16`）格式处理数据  
    - 每个元素占2字节（影响内存布局计算）
4. **寄存器管理**  
    - 输入寄存器 `T#4` 添加了 `.reuse` 标记，表示**执行后保留该寄存器**
    - 输入寄存器 `T#1` **执行后自动释放**（无reuse标记）  
    - 输出寄存器分配 `512B` 空间（足够存储计算结果）
5. **特殊处理**  
    - 区域中**超出有效范围的部分**不初始化（`PadValue` 缺省）  
    - 输出寄存器由硬件自动分配（`->T` 未指定具体寄存器号）

---

## 备注

此指令是TileOp模版块，软件只定义块头。
