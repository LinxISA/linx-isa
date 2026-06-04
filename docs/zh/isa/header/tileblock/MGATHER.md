# MGATHER

## 说明

**内存聚集（Gather from Memory to Tile）**

`MGATHER` 是一条基于间接寻址的数据聚集指令。它以基地址寄存器（`RegSrc`）为内存起始地址，以输入 Tile（`SrcTile`）中存储的一组偏移量（offset）为索引，从离散的内存位置逐一读取数据元素，并按 offset 在 SrcTile 中的行列顺序连续写入输出 Tile（`DstTile`）的对应位置，从而将稀疏分布的内存数据聚合为稠密的二维 Tile 数据块。

该指令的核心语义可以理解为：对于 SrcTile 中位于 `(i, j)` 处的 offset 值 `off`，从内存地址 `baseAddress + off` 处读取一个 `DataType` 类型的数据元素，并将其写入 DstTile 的 `(i, j)` 位置。这一过程遍历 `validRow × validCol` 的有效区域，逐元素独立执行。 

## 汇编语法

```asm
MGATHER <LB0:validCol, LB1:validRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, [RegSrc], ->DstTile<Size>
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|-----|-----------|
| **validCol** | 有效列数，表示输出Tile中有效数据的列数，也是输入Tile中有效offset的列数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB0寄存器。 | 否 |
| **validRow** | 有效行数，表示输出Tile中有效数据的行数，也是输入Tile中有效offset的行数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB1寄存器。 | 是，默认为1 |
| **Col** | 输出Tile寄存器中一行元素的总列数（包含无效列）。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB2寄存器。 | 是，默认等于validCol |
| **Row** | 输出Tile寄存器中一列的总行数（包含无效行）。该值由硬件通过 `TileSize / (Col * sizeof(DataType))` 计算得到，无需软件显式设置。 | 否（硬件推导） |
| **DataType** | 从内存中收集的元素的数据类型/格式。 | 否 |
| **PadValue** | DstTile 中位于有效区域之外的填充值。可选类型包括：`Null`（不填充或保留随机值）、`Zero`（填充零值）、`Max`（填充当前数据格式下的最大值）、`Min`（填充当前数据格式下的最小值）。 | 是，默认 Null |
| **RegSrc** | 输入全局寄存器GGPR，用于存储收集数据的内存基地址baseAddress。 | 否 |
| **SrcTile** | 输入Tile 寄存器，用于存储一组基于baseAddress的偏移(offset)。 | 否 |
| **DstTile** | 输出Tile 寄存器，用于存储聚集得到的数据。 | 否 |
| **Size** | 指示输出Tile寄存器的大小。该值等于Row * Col * sizeof(DataType) | 否 |

其中DataType的可选类型如下表：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | S64, U64, FP64 |
| b32 | S32, U32, FP32, TF32, HF32 |
| b16 | S16, U16, FP16, BF16 |
| b8  | S8,  U8,  FP8(E4M3, E5M2), E8M0, HiF8, HiF4x2, E1M2x2, E2M1x2, S4x2, U4x2 |

---

## 编码格式

该TileOp编码为以下指令：

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `MGATHER, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue` *（注：可缺省该指令）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` *（注：validCol）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` *（注：validRow）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2` *（注：Col，可缺省该指令）*
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc` *（注：base）*

---

## 执行模型

本指令执行过程通过伪代码示意如下：

```c
// dst：用于存储聚集数据的输出Tile
// base: 收集数据的基地址
// src: 存储离散的地址偏移的输入Tile
void MGATHER(Tile __out__ dst, Scalar __in__ base, Tile __in__ src) {
  for (int i = 0; i < Row; i++)
    for (int j = 0; j < Col; j++) {
      if (i < validRow && j < validCol) {
        offset_t offset = src[i][j];  // offset宽度由src的元素位宽决定（u64/u32/u16）
        dst[i][j] = Memory[base + offset];
      } else {
        dst[i][j] = PadValue;         // 填充区域写入PadValue
      }
    }
}
```

图示如下：

![MGATHER](../../../figs/isa/tileop/MGATHER.png){ width="800" }

## 注意事项

- `validCol` 必须小于等于 `Col`，即有效列数不超过一行的总列数。
- `validRow` 必须小于等于 `Row`，即有效行数不超过一列的总行数。
- `Row` 由硬件根据 `Size / (Col * sizeof(DataType))` 自动推导，因此 `Size` 必须是 `Col * sizeof(DataType)` 的整数倍。
- 输入数据块（SrcTile）中仅 `[0, validRow) × [0, validCol)` 范围内的 offset 元素参与聚集操作；DstTile 中超出该有效范围的填充区域写入 `PadValue`。
- SrcTile 中 offset 的位宽取决于写入该 Tile 时的元素位宽定义，支持 **u64**、**u32** 或 **u16** 格式，硬件根据 SrcTile 的实际元素位宽进行解析。
