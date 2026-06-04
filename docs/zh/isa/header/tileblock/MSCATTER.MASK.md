# MSCATTER.MASK

## 说明

**带掩码的内存分散（Masked Scatter from Tile to Memory）**

`MSCATTER.MASK` 是 `MSCATTER` 的掩码变体，在其间接寻址分散语义的基础上增加了逐元素谓词控制。除基地址寄存器（`RegSrc`）、数据 Tile（`SrcTile0`）和偏移量 Tile（`SrcTile1`）外，该指令额外接受一个掩码 Tile（`MaskTile`），其中每个元素为 1 bit 的标志位，与 SrcTile0/SrcTile1 中的元素一一对应。

执行时，对于 `(i, j)` 位置，硬件首先检查 MaskTile 对应位置的掩码位：
- 若掩码为 `1`，则执行分散操作：从 SrcTile1 读取偏移量 `off`，将 SrcTile0 中 `(i, j)` 处的数据元素写入内存地址 `baseAddress + off`；
- 若掩码为 `0`，则跳过该位置，不产生内存访问。

这一机制允许软件通过掩码动态控制哪些位置的数据参与分散，适用于需要条件性数据写入的场景（如仅更新稀疏矩阵中的非零元素）。

## 汇编语法

```asm
MSCATTER.MASK <LB0:Col, LB1:Row, DataType>, SrcTile0<.reuse>, SrcTile1<.reuse>, MaskTile<.reuse>, [RegSrc]
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|-----|-----------|
| **Col** | Tile寄存器中数据的列数，也是输入Tile中offset的列数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB0寄存器。 | 否 |
| **Row** | Tile寄存器中数据的行数，也是输入Tile中offset的行数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB1寄存器。 | 是，默认为1 |
| **DataType** | 输入Tile中数据的格式，即向内存中散布的元素的数据类型/格式。 | 否 |
| **RegSrc**   | 输入全局寄存器GGPR，用于存储分散数据的内存基地址baseAddress。 | 否 |
| **SrcTile0** | 第一个输入Tile 寄存器，用于存储源数据。 | 否 |
| **SrcTile1** | 第二个输入Tile 寄存器，用于存储偏移量（offset）。 | 否 |
| **MaskTile** | 输入Tile 寄存器，用于存储掩码标志位。每个元素为1bit，值为`1`表示对应位置执行分散操作；值为`0`表示跳过该位置，不产生内存访问。 | 否 |

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

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `MSCATTER.MASK, DataType`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` *（注：Col）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` *（注：Row）*
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>`
- [B.IOT](../../header/B.IOT.md) `MaskTile<.reuse>, last`
- [B.IOR](../../header/B.IOR.md) `RegSrc` *（注：base）*

---

## 执行模型

本指令执行过程通过伪代码示意如下：

```c
// src0: 存储数据的输入Tile
// base: 表示基地址的标量
// src1: 存储偏移的输入Tile
// mask: 存储掩码标志位的输入Tile，1bit/元素
void MSCATTER_MASK(Tile __in__ src0, Scalar __in__ base, Tile __in__ src1, Tile __in__ mask) {
  for (int i = 0; i < Row; i++)
    for (int j = 0; j < Col; j++) {
      if (mask[i][j] == 1) {
        offset_t offset = src1[i][j];  // offset宽度由src1的元素位宽决定（u64/u32/u16）
        Memory[base + offset] = src0[i][j];
      }
    }
}
```

## 注意事项

- SrcTile0 的大小必须等于 `Row * Col * sizeof(DataType)`。
- 输入数据块（SrcTile0 和 SrcTile1）中 `[0, Row) × [0, Col)` 范围内的所有元素均参与分散操作。
- SrcTile1 中 offset 的位宽取决于写入该 Tile 时的元素位宽定义，支持 **u64**、**u32** 或 **u16** 格式，硬件根据 SrcTile1 的实际元素位宽进行解析。
- 输入掩码Tile（MaskTile）中每个元素为 **1 bit**，与 SrcTile0/SrcTile1 的 `[0, Row) × [0, Col)` 区域一一对应。掩码值为 `1` 时执行对应位置的分散，为 `0` 时跳过该位置，不产生内存访问。
- 如果多个未被掩码屏蔽的元素映射到同一目标内存地址，最终值由实现定义。
