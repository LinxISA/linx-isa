# MGATHER

## 说明

**内存聚集（Gather from Memory to Tile）**

`MGATHER` 是一条基于间接寻址的数据聚集指令。它以基地址寄存器
（`RegSrc`）为内存起始地址，以输入 Tile（`SrcTile`）中存储的一组偏移量
（offset）为索引，从离散的内存位置逐一读取数据元素，并按 offset 在
`SrcTile` 中的行列顺序连续写入输出 Tile（`DstTile`）的对应位置，从而将
稀疏分布的内存数据聚合为稠密的二维 Tile 数据块。

该指令只对 `[0, validRow) x [0, validCol)` 的有效区域执行访存；超出有效
区域的输出位置写入 `PadValue`。

## 汇编语法

```asm
MGATHER <LB0:validCol, LB1:validRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, [RegSrc], ->DstTile<Size>
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|-----|-----------|
| **validCol** | 有效列数，表示输出 Tile 中有效数据的列数，也是输入 Tile 中有效 offset 的列数。该值通过 `LB0` 传入。 | 否 |
| **validRow** | 有效行数，表示输出 Tile 中有效数据的行数，也是输入 Tile 中有效 offset 的行数。该值通过 `LB1` 传入。 | 是，默认为 1 |
| **Col** | 输出 Tile 每行的物理列数（包含填充列）。该值通过 `LB2` 传入。 | 是，默认等于 `validCol` |
| **Row** | 输出 Tile 的物理行数（包含填充行）。硬件通过 `Size / (Col * sizeof(DataType))` 自动推导。 | 否（硬件推导） |
| **DataType** | 从内存中收集的元素的数据类型/格式。 | 否 |
| **PadValue** | DstTile 中位于有效区域之外的填充值。可选值为 `Null`、`Zero`、`Max`、`Min`。 | 是，默认 `Null` |
| **RegSrc** | 输入全局寄存器 GGPR，用于存储收集数据的内存基地址 `baseAddress`。 | 否 |
| **SrcTile** | 输入 Tile 寄存器，用于存储一组基于 `baseAddress` 的偏移量。 | 否 |
| **DstTile** | 输出 Tile 寄存器，用于存储聚集得到的数据。 | 否 |
| **Size** | 输出 Tile 的大小，必须等于 `Row * Col * sizeof(DataType)`。 | 否 |

`SrcTile` 中 offset 的位宽由写入该 Tile 时使用的元素位宽决定，规范形式
支持 `u16`、`u32` 和 `u64`。

## 编码格式

该 TileOp 编码为以下指令：

- [BSTART.MGATHER](../../blockIntro/tma_block/header.md) `DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue` *（可选）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` *（`validCol`）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` *（`validRow`）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2` *（`Col`，可选）*
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

## 执行模型

```c
void MGATHER(Tile dst, Scalar base, Tile src) {
  for (int i = 0; i < Row; ++i) {
    for (int j = 0; j < Col; ++j) {
      if (i < validRow && j < validCol) {
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

- `validCol <= Col`，`validRow <= Row`。
- `Size` 必须是 `Col * sizeof(DataType)` 的整数倍。
- 超出有效区域的位置不产生访存，直接写入 `PadValue`。
