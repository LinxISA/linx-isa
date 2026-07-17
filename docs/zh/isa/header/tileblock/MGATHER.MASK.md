# MGATHER.MASK

## 说明

**带掩码的内存聚集（Masked Gather from Memory to Tile）**

`MGATHER.MASK` 是 `MGATHER` 的掩码变体，在其间接寻址聚集语义的基础上
增加了逐元素谓词控制。除基地址寄存器（`RegSrc`）和偏移量 Tile
（`SrcTile`）外，该指令额外接受一个掩码 Tile（`MaskTile`），其中每个
元素为 1 bit 的标志位，与 `SrcTile` 中的 offset 一一对应。

当掩码位为 `1` 时，硬件从 `baseAddress + offset` 读取一个 `DataType`
元素并写入 `DstTile`；当掩码位为 `0` 时，硬件跳过该位置的访存，并向
目标位置写入 `PadValue`。

## 汇编语法

```asm
MGATHER.MASK <LB0:Col, LB1:Row, DataType, PadValue>, SrcTile<.reuse>, MaskTile<.reuse>, [RegSrc], ->DstTile<Size>
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|-----|-----------|
| **Col** | Tile 中数据的列数，也是输入 Tile 中 offset 的列数。通过 `LB0` 传入。 | 否 |
| **Row** | Tile 中数据的行数，也是输入 Tile 中 offset 的行数。通过 `LB1` 传入。 | 是，默认为 1 |
| **DataType** | 从内存中收集的元素的数据类型/格式。 | 否 |
| **PadValue** | 掩码为 `0` 时写入目标 Tile 的填充值。可选值为 `Null`、`Zero`、`Max`、`Min`。 | 是，默认 `Null` |
| **RegSrc** | 输入全局寄存器 GGPR，用于存储收集数据的内存基地址 `baseAddress`。 | 否 |
| **SrcTile** | 输入 Tile 寄存器，用于存储一组基于 `baseAddress` 的偏移量。 | 否 |
| **MaskTile** | 输入 Tile 寄存器，用于存储 1 bit 掩码。 | 否 |
| **DstTile** | 输出 Tile 寄存器，用于存储聚集得到的数据。 | 否 |
| **Size** | 输出 Tile 的大小，必须等于 `Row * Col * sizeof(DataType)`。 | 否 |

`SrcTile` 中 offset 的位宽由写入该 Tile 时使用的元素位宽决定，规范形式
支持 `u16`、`u32` 和 `u64`。

## 编码格式

该 TileOp 编码为以下指令：

- [BSTART.MGATHER.MASK](../../blockIntro/tma_block/header.md) `DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue` *（可选）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` *（`Col`）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` *（`Row`）*
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, MaskTile<.reuse>, last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

## 执行模型

```c
void MGATHER_MASK(Tile dst, Scalar base, Tile src, Tile mask) {
  for (int i = 0; i < Row; ++i) {
    for (int j = 0; j < Col; ++j) {
      if (mask[i][j] == 1) {
        offset_t offset = src[i][j];
        dst[i][j] = Memory[base + offset];
      } else {
        dst[i][j] = PadValue;
      }
    }
  }
}
```

## 注意事项

- `MaskTile` 按每元素 1 bit 解释。
- 掩码为 `0` 的位置不产生访存。
