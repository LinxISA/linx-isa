# MSCATTER

## 说明

**内存分散（Scatter from Tile to Memory）**

`MSCATTER` 是 `MGATHER` 的逆操作，基于间接寻址将稠密的二维 Tile 数据分散
写入离散的内存位置。它以基地址寄存器（`RegSrc`）为内存起始地址，以
偏移量 Tile（`SrcTile1`）中的 offset 为索引，将数据 Tile（`SrcTile0`）
中的元素写入 `baseAddress + offset`。

该指令只对 `[0, validRow) x [0, validCol)` 的有效区域执行写入。

## 汇编语法

```asm
MSCATTER <LB0:validCol, LB1:validRow, LB2:Col, DataType>, SrcTile0<.reuse>, SrcTile1<.reuse>, [RegSrc]
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|------|------------|
| **validCol** | 有效列数，表示输入数据 Tile 和 offset Tile 的有效列数。该值通过 `LB0` 传入。 | 否 |
| **validRow** | 有效行数，表示输入数据 Tile 和 offset Tile 的有效行数。该值通过 `LB1` 传入。 | 是，默认为 1 |
| **Col** | 输入 Tile 每行的物理列数（包含无效列）。该值通过 `LB2` 传入。 | 是，默认等于 `validCol` |
| **Row** | 输入 Tile 的物理行数（包含无效行）。硬件通过 `SrcTile0.Size / (Col * sizeof(DataType))` 自动推导。 | 否（硬件推导） |
| **DataType** | 向内存中写入的元素的数据类型/格式。 | 否 |
| **RegSrc**   | 输入全局寄存器 GGPR，用于存储分散数据的内存基地址 `baseAddress`。 | 否 |
| **SrcTile0** | 第一个输入 Tile 寄存器，用于存储源数据。 | 否 |
| **SrcTile1** | 第二个输入 Tile 寄存器，用于存储偏移量（offset）。 | 否 |

`SrcTile1` 中 offset 的位宽由写入该 Tile 时使用的元素位宽决定，规范形式
支持 `u16`、`u32` 和 `u64`。

## 编码格式

该 TileOp 编码为以下指令：

- [BSTART.MSCATTER](../../blockIntro/tlsu_block/header.md) `DataType`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` *（`validCol`）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` *（`validRow`）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2` *（`Col`，可选）*
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, last`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

## 执行模型

```c
void MSCATTER(Tile src0, Scalar base, Tile src1) {
  for (int i = 0; i < validRow; ++i) {
    for (int j = 0; j < validCol; ++j) {
      offset_t offset = src1[i][j];
      Memory[base + offset] = src0[i][j];
    }
  }
}
```

## 注意事项

- `validCol <= Col`，`validRow <= Row`。
- `SrcTile0.Size` 必须是 `Col * sizeof(DataType)` 的整数倍。
- 如果多个有效元素映射到同一目标地址，最终值由实现定义。
