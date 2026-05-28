# MSCATTER

## 说明

**内存分散（Scatter from Tile to Memory）**

`MSCATTER` 是 `MGATHER` 的逆操作，基于间接寻址将稠密的二维 Tile 数据分散写入离散的内存位置。它以基地址寄存器（`RegSrc`）为内存起始地址，以偏移量 Tile（`SrcTile1`）中存储的偏移量（offset）为索引，将数据 Tile（`SrcTile0`）中的每个元素写入对应的内存地址 `baseAddress + off`。

该指令的核心语义可以理解为：对于 `(i, j)` 位置，从 SrcTile1 读取偏移量 `off`，将 SrcTile0 中 `(i, j)` 处的数据元素写入内存地址 `baseAddress + off`。这一过程遍历 `validRow × validCol` 的有效区域，逐元素独立执行。

## 汇编语法

```asm
MSCATTER <LB0:validCol, LB1:validRow, LB2:Col, DataType>, SrcTile0<.reuse>, SrcTile1<.reuse>, [RegSrc]
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|------|------------|
| **validCol** | 有效列数，表示输入Tile中有效数据的列数，也是输入Tile中有效offset的列数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB0寄存器。 | 否 |
| **validRow** | 有效行数，表示输入Tile中有效数据的行数，也是输入Tile中有效offset的行数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB1寄存器。 | 是，默认为1 |
| **Col** | 输入Tile寄存器中一行元素的总列数（包含无效列）。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB2寄存器。 | 是，默认等于validCol |
| **Row** | 输入Tile寄存器中一列的总行数（包含无效行）。该值由硬件通过 `SrcTile0的Size / (Col * sizeof(DataType))` 计算得到，无需软件显式设置。 | 否（硬件推导） |
| **DataType** | 输入Tile中数据的格式，即向内存中散布的元素的数据类型/格式。 | 否 |
| **RegSrc**   | 输入全局寄存器GGPR，用于存储分散数据的内存基地址baseAddress。 | 否 |
| **SrcTile0** | 第一个输入Tile 寄存器，用于存储源数据。 | 否 |
| **SrcTile1** | 第二个输入Tile 寄存器，用于存储偏移量（offset）。  | 否 |

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

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `MSCATTER, DataType`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` *（注：validCol）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` *（注：validRow）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2` *（注：Col）*
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, last`
- [B.IOR](../../header/B.IOR.md) `RegSrc` *（注：base）*

---

## 执行模型

本指令执行过程通过伪代码示意如下：

```c
// src0: 存储数据的输入Tile
// base: 表示基地址的标量
// src1: 存储偏移的输入Tile
void MSCATTER(Tile __in__ src0, Scalar __in__ base, Tile __in__ src1) {
  for (int i = 0; i < validRow; i++)
    for (int j = 0; j < validCol; j++) {
      offset_t offset = src1[i][j];  // offset宽度由src1的元素位宽决定（u64/u32/u16）
      Memory[base + offset] = src0[i][j];
    }
}
```

实现示意图如下：

![MSCATTER](../../../figs/isa/tileop/MSCATTER.png){ width="800" }

## 注意事项

- `validCol` 必须小于等于 `Col`，即有效列数不超过一行的总列数。
- `validRow` 必须小于等于 `Row`，即有效行数不超过一列的总行数。
- `Row` 由硬件根据 `SrcTile0的Size / (Col * sizeof(DataType))` 自动推导，因此 SrcTile0 的 Size 必须是 `Col * sizeof(DataType)` 的整数倍。
- 输入数据块（SrcTile0 和 SrcTile1）中仅 `[0, validRow) × [0, validCol)` 范围内的元素参与分散操作，超出该范围的元素行为未定义。
- SrcTile1 中 offset 的位宽取决于写入该 Tile 时的元素位宽定义，支持 **u64**、**u32** 或 **u16** 格式，硬件根据 SrcTile1 的实际元素位宽进行解析。
- 如果多个元素映射到同一目标内存地址，最终值由实现定义。
