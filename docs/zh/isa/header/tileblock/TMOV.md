# TMOV

## 说明

**数据块移动(Tile Move)**

`TMOV` 将输入 Tile 的数据移动/复制到输出 Tile 中，并支持对数据存储布局（分形）进行变换。

实现伪代码示意如下：
```pseudocode
// 逐元素移动操作
for r in 0..(Rv-1):          // 遍历所有行
  for r in 0..(Cv-1):        // 遍历所有列
    dst[r, c] = src[r, c]       // 逐元素复制
```

实现示意图如下：

![TMOV](../../../figs/isa/tileop/TMOV.png){ width="800" }

---

## 汇编语法

```asm
    TMOV Layout, <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, ->DstTile<Size>
```

## 汇编符号

- **Layout**：指示数据移动过程中存储布局的变换方式，例如`NORM`, `NZ2ND`，`NZ2DN`等。
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

本指令支持的数据格式（DataType）如下表所示：

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

---

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `TMOV, DataType`
- [B.DATR](../../header/B.DATR.md) `Layout, PadValue`
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
- **数据类型**：
    - `SrcTile::DataType == DstTile::DataType`
- **存储布局**：
    - 输入/输出 Tile 必须是**行主序（RowMajor）**。
- **尺寸范围**：
    - Tile的行列/有效行列等参数大小均必须小于等于16bit。

---

## 汇编示例

示例1：**ND格式转换为NZ格式**
```asm
TMOV ND2NZ, <LB0:32, LB1:16, fp16> T#1.reuse, ->T<1KB>
```
示例2：**NZ格式转换为ZN格式**
```asm
TMOV NZ2ZN, <LB0:30, LB1:16, LB2:32, fp16> T#2, ->U<1KB>
```

NZ格式转换为ZN格式

![TMOV_NZ2ZN](../../../figs/isa/tileop/TMOV_NZ2ZN.png){ width="800" }

---

## 备注

此指令是TileOp模版块，软件只定义块头。
