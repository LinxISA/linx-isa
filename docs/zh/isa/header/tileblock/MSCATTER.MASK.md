# MSCATTER.MASK

## 说明

**带掩码的内存分散（Masked Scatter from Tile to Memory）**

`MSCATTER.MASK` 是 `MSCATTER` 的掩码变体，在其间接寻址分散语义的基础上
增加了逐元素谓词控制。除基地址寄存器（`RegSrc`）、数据 Tile
（`SrcTile0`）和偏移量 Tile（`SrcTile1`）外，该指令额外接受一个掩码
Tile（`MaskTile`），其中每个元素为 1 bit 的标志位。

当掩码位为 `1` 时，硬件从 `SrcTile1` 读取偏移量 `off`，并将
`SrcTile0` 的数据写入 `baseAddress + off`；当掩码位为 `0` 时，硬件跳过
该位置的写入。

## 汇编语法

```asm
MSCATTER.MASK <LB0:Col, LB1:Row, DataType>, SrcTile0<.reuse>, SrcTile1<.reuse>, MaskTile<.reuse>, [RegSrc]
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|-----|-----------|
| **Col** | Tile 中数据和 offset 的列数。通过 `LB0` 传入。 | 否 |
| **Row** | Tile 中数据和 offset 的行数。通过 `LB1` 传入。 | 是，默认为 1 |
| **DataType** | 向内存中分散写入的元素的数据类型/格式。 | 否 |
| **RegSrc** | 输入全局寄存器 GGPR，用于存储分散数据的内存基地址 `baseAddress`。 | 否 |
| **SrcTile0** | 第一个输入 Tile 寄存器，用于存储源数据。 | 否 |
| **SrcTile1** | 第二个输入 Tile 寄存器，用于存储偏移量（offset）。 | 否 |
| **MaskTile** | 输入 Tile 寄存器，用于存储 1 bit 掩码。 | 否 |

`SrcTile1` 中 offset 的位宽由写入该 Tile 时使用的元素位宽决定，规范形式
支持 `u16`、`u32` 和 `u64`。

## 编码格式

该 TileOp 编码为以下指令：

- [BSTART.MSCATTER.MASK](../../blockIntro/tma_block/header.md) `DataType`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` *（`Col`）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` *（`Row`）*
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, MaskTile<.reuse>, last`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

## 执行模型

```c
void MSCATTER_MASK(Tile src0, Scalar base, Tile src1, Tile mask) {
  for (int i = 0; i < Row; ++i) {
    for (int j = 0; j < Col; ++j) {
      if (mask[i][j] == 1) {
        offset_t offset = src1[i][j];
        Memory[base + offset] = src0[i][j];
      }
    }
  }
}
```

## 注意事项

- `MaskTile` 按每元素 1 bit 解释。
- 如果多个有效元素映射到同一目标地址，最终值由实现定义。
