# MGATHER.MASK

## 说明

**带掩码的内存聚集（Masked Gather from Memory to Tile）**

`MGATHER.MASK` 是 `MGATHER` 的掩码变体，在其间接寻址聚集语义的基础上增加了逐元素谓词控制。除基地址寄存器（`RegSrc`）和偏移量 Tile（`SrcTile`）外，该指令额外接受一个掩码 Tile（`MaskTile`），其中每个元素为 1 bit 的标志位，与 SrcTile 中的 offset 一一对应。

执行时，对于 SrcTile 中位于 `(i, j)` 处的 offset 值 `off`，硬件首先检查 MaskTile 对应位置的掩码位：
- 若掩码为 `1`，则执行聚集操作：从内存地址 `baseAddress + off` 处读取一个 `DataType` 类型的数据元素，写入 DstTile 的 `(i, j)` 位置；
- 若掩码为 `0`，则跳过该位置，不产生内存访问，DstTile 的 `(i, j)` 位置写入 `PadValue` 填充值。

这一机制允许软件通过掩码动态控制哪些内存位置参与聚集，适用于需要条件性数据收集的场景（如稀疏矩阵中仅加载非零元素对应的数据）。

## 汇编语法

```asm
MGATHER.MASK <LB0:Col, LB1:Row, DataType, PadValue>, SrcTile<.reuse>, MaskTile<.reuse>, [RegSrc], ->DstTile<Size>
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|-----|-----------|
| **Col** | Tile寄存器中数据的列数，也是输入Tile中offset的列数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB0寄存器。 | 否 |
| **Row** | Tile寄存器中数据的行数，也是输入Tile中offset的行数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB1寄存器。 | 是，默认为1 |
| **DataType** | 从内存中收集的元素的数据类型/格式。 | 否 |
| **PadValue** | DstTile 中掩码为 `0` 的位置的填充值。可选类型包括：`Null`（不填充或保留随机值）、`Zero`（填充零值）、`Max`（填充当前数据格式下的最大值）、`Min`（填充当前数据格式下的最小值）。 | 是，默认 Null |
| **RegSrc** | 输入全局寄存器GGPR，用于存储收集数据的内存基地址baseAddress。 | 否 |
| **SrcTile** | 输入Tile 寄存器，用于存储一组基于baseAddress的偏移(offset)。 | 否 |
| **MaskTile** | 输入Tile 寄存器，用于存储掩码标志位。每个元素为1bit，值为`1`表示对应offset有效，执行聚集操作；值为`0`表示对应offset无效，跳过聚集。 | 否 |
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

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `MGATHER.MASK, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue` *（注：可缺省该指令）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` *（注：Col）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` *（注：Row）*
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, MaskTile<.reuse>, last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc` *（注：base）*

---

## 执行模型

本指令执行过程通过伪代码示意如下：

```c
// dst：用于存储聚集数据的输出Tile
// base: 收集数据的基地址
// src: 存储离散的地址偏移的输入Tile
// mask: 存储掩码标志位的输入Tile，1bit/元素
void MGATHER_MASK(Tile __out__ dst, Scalar __in__ base, Tile __in__ src, Tile __in__ mask) {
  for (int i = 0; i < Row; i++)
    for (int j = 0; j < Col; j++) {
      if (mask[i][j] == 1) {
        offset_t offset = src[i][j];  // offset宽度由src的元素位宽决定（u64/u32/u16）
        dst[i][j] = Memory[base + offset];
      } else {
        dst[i][j] = PadValue;         // 掩码为0的位置写入PadValue
      }
    }
}
```

## 注意事项

- `Size` 必须等于 `Row * Col * sizeof(DataType)`。
- 输入数据块（SrcTile）中 `[0, Row) × [0, Col)` 范围内的所有 offset 元素均参与聚集操作。
- SrcTile 中 offset 的位宽取决于写入该 Tile 时的元素位宽定义，支持 **u64**、**u32** 或 **u16** 格式，硬件根据 SrcTile 的实际元素位宽进行解析。
- 输入掩码Tile（MaskTile）中每个元素为 **1 bit**，与 SrcTile 的 `[0, Row) × [0, Col)` 区域一一对应。掩码值为 `1` 时执行对应位置的聚集，为 `0` 时跳过该位置，不产生内存访问，对应位置写入 `PadValue` 填充值。
