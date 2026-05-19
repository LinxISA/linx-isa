# TCVT

## 说明

**数据块类型转换（Tile Convert）**

`TCVT` 用于对输入 Tile 进行逐元素的数据类型转换，结果写入输出 Tile 中。

实现伪代码示意如下：
```pseudocode
// 逐元素转换操作
for r in 0..(Rv-1):          // 遍历所有行
  for r in 0..(Cv-1):        // 遍历所有列
    dst[r, c] = Convert(src[r, c])      // 逐元素转换，遵守舍入模式和饱和计算要求
```

实现示意图如下：

![TCVT](../../../figs/isa/tileop/TCVT.png){ width="800" }

---

## 汇编语法

```asm
TCVT <LB0:ValidCol, LB1:ValidRow, LB2:Col, SrcType, DstType, PadValue, RMode, Sat>, SrcTile<.reuse>, ->DstTile<Size>
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
- **SrcType**：输入Tile内元素的数据格式，支持类型见下表。
- **DstType**：输出Tile内元素的数据格式，支持类型见下表。
- **PadValue**：输出Tile无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。
- **RMode**：舍入模式参数，可选模式见下表。
- **Sat**：饱和运算标志，可缺省。（缺省表示不支持饱和运算或由实现/硬件针对特定类型定义饱和行为）
- **SrcTile0/SrcTile1**：输入Tile寄存器，支持`T`/`U`/`M`/`N`队列输入（参见：[Tile寄存器](../../register/common/tilereg.md)）。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：输出Tile寄存器，支持`T`/`U`/`M`/`N`队列输出。
- **Size**：输出Tile寄存器的空间大小（有效范围参见：[Tile寄存器](../../register/common/tilereg.md)）。

本指令支持的源格式（SrcType）和目标格式（DstType）如下表所示：

| Datatype | 说明 | Datatype | 说明 |
|----------|------|----------|-------|
| FP64 | 64位双精度浮点数（E11M52） | S64 | 64位有符号整型数据 |
| FP32 | 32位单精度浮点数（E8M23） | S32 | 32位有符号整型数据 |
| TF32 | 32位单精度浮点数（E8M10） | S16 | 16位有符号整型数据 |
| HF32 | 32位单精度浮点数（E8M11） | S8 | 8位有符号整型数据 |
| FP16 | 16位半精度浮点数（E5M10） | S4x2 | 两个4位有符号整型数据 |
| BF16 | 16位半精度浮点数（E8M7） | U64 | 64位无符号整型数据 |
| E4M3 | 8位低精度浮点数（E4M3） | U32 | 32位无符号整型数据 |
| E5M2 | 8位低精度浮点数（E5M2） | U16 | 16位无符号整型数据 |
| E2M3 | 6位低精度浮点数（E2M3） | U8 | 8位无符号整型数据 |
| E3M2 | 6位低精度浮点数（E3M2） | U4x2 | 两个4位无符号整型数据 |
| HiF8 | 8位低精度浮点数（E8M0） | HiF4x2 | 两个4位低精度浮点数（E1M2） |
| E2M1x2 | 两个4位低精度浮点数（E2M1） | E1M2x2 | 两个4位低精度浮点数（E1M2） |
| E8M0 | 8位低精度浮点数 | / | / |

本指令支持的舍入模式如下表所示：

| 舍入模式 | 含义 |
|----------|---------|
| **RNONE** | No Rounding（不指定舍入模式，由硬件/实现决定默认行为） |
| **RNE** | Round to Nearest, ties to Even（向最近偶数舍入；最常见） |
| **RTZ** | Round Toward Zero（向零舍入，截断小数部分） |
| **RDN** | Round Down（向负无穷舍入） |
| **RUP** | Round Up（向正无穷舍入） |
| **RNA** | Round to Nearest, ties Away from Zero（远离零） |
| **RTO** | Round to Odd（向最近奇数舍入） |
| **RHB** | Hybrid Rounding（混合舍入模式） |

---

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TCVT, SrcType`
- [B.DATR](../../header/B.DATR.md) `DstType, RMode, Sat`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **动态参数**：
    - `SrcTile::ValidCol == DstTile::ValidCol`
    - `SrcTile::ValidRow == DstTile::ValidRow`
- **有效边界**：
    - `ValidRow <= Row`, `ValidCol <= Col`
- **存储布局**：
    - 输入/输出 Tile 必须是**行主序（RowMajor）**。
- **尺寸范围**：
    - Tile的行列/有效行列等参数大小均必须小于等于16bit。

---

## 低精度数据格式转换

TCVT 指令执行 `高精度数据格式`（如 fp16）向 `打包低精度格式dtypex2`（如 e2m1x2）的转换。该过程的核心操作步骤如下，作用于输入 Tile 有效区域 (ValidRow x ValidCol) 内的 每一个高精度元素：

1. **数值转换**：
    * 根据源高精度数据类型 (SrcType) 和目标低精度 `dtypex2` (DstType) 的规范，将高精度元素的数值转换为对应的低精度数值表示。
    * 此步骤涉及位宽缩减和可能的数值域映射（如浮点数转自定义低位浮点数或整数）。
2. **可选饱和处理 (Sat 模式)**：
    * 如果启用了饱和标志 (Sat=1)：
    * 检查转换后的低精度数值是否超出目标 `dtypex2` 格式的可表示范围 [MinValue, MaxValue]。
    * 若转换结果 > MaxValue，则将结果钳位到 MaxValue。
    * 若转换结果 < MinValue，则将结果钳位到 MinValue。
    * 如果未启用饱和 (Sat=0)，则跳过此步，转换结果直接进入下一步（可能溢出）。
3. 可选**舍入处理 (RMode 模式)**：
    * 在数值转换过程中（尤其是浮点转浮点或浮点转整数时），如果源值无法精确表示为目标格式，需要进行舍入。
    * 根据指定的舍入模式 (RMode)，对转换结果进行修正，选择最接近或符合规则的可表示值。
4. **4-bit 元素生成**：
    * 经过以上步骤，得到一个符合目标 dtypex2 格式规范的 4-bit 数值。
5. **4-bit 元素打包** (关键步骤)：
    * 核心操作：硬件自动将连续两个由上述步骤生成的 4-bit 元素 打包组合到 1 个字节 (8 bit) 中。
    * 打包规则：
    * 假设元素 i 和元素 i+1 是转换后相邻的两个 4-bit 值。
    * 这两个 4-bit 值 (elem_i 和 elem_i+1) 会被合并存储在一个物理字节单元内。
    * 具体的位序（是 [elem_i+1, elem_i] 还是 [elem_i, elem_i+1]）由硬件架构定义。

目的：此打包操作避免了在后续内存或寄存器访问中出现低效或非法的半字节 (4-bit) 非对齐访问，并将两个元素紧密存储在 1 字节内，提高了存储密度和存取效率。

结果：输入有效区域内的 `M x N` 个高精度元素，被转换为 `M x N` 个 4-bit 低精度元素。这些低精度元素以**打包形式**存储在输出 Tile 的有效区域中，物理上占据M x (N / 2)个字节单元（即 `列数Col和有效列数ValidCol` 减半）。每个字节单元包含两个逻辑元素。

![TCVT_FP162E1M2](../../../figs/isa/tileop/TCVT_FP162E1M2.png){ width="800" }

## 饱和运算

饱和计算用于限制计算结果的范围，防止数值溢出。例如，在机器学习推理、图像处理或归一化操作中，经常需要将输出限定在 [MinValue, MaxValue] 区间内。

当指令中添加 `sat` 标志时，浮点运算结果会自动应用如下限制逻辑：
```py
if result > MaxValue: result = MaxValue
if result < MinValue: result = MinValue
```
MaxValue表示当前数据格式的最大值，MinValue表示当前数据格式的最小值。

## 汇编示例

示例1：`fp32 -> fp16` ; `RMode::RNE`; 支持饱和运算
```asm
TCVT <LB0:50, LB1:32, LB2:64, fp32, fp16, RNE, Sat>, T#3, ->T<4KB>
```
示例2：`fp16 -> e2m1x2` ; `RMode::RNA`; 默认不支持饱和运算
```asm
TCVT <LB0:32, LB1:16, fp16, e2m1x2, RNA>, T#2, ->T<256B>
```

---

## 备注

此指令是TileOp模版块，软件只定义块头。
