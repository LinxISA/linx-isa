# MGATHER.CAS

## 说明

**聚集比较交换（Gather Compare-And-Swap）**

`MGATHER.CAS` 是 v0.57 新增的 TMA 原子访存操作。它以基地址寄存器
（`RegSrc`）和 offset Tile（`SrcTile0`）形成一组离散地址；对每个有效元素，
硬件读取旧值，与 expected Tile（`SrcTile1`）中的期望值比较，相等时写入
desired Tile（`SrcTile2`）中的新值。无论比较是否成功，旧值都写入目标 Tile
（`DstTile`）。

第一个 [B.IOR](../../header/B.IOR.md) 输入寄存器保存内存基地址。该操作不使用
已退役的目的地专用描述符拼写。

## 汇编语法

```asm
MGATHER.CAS <LB0:Col, LB1:Row, DataType>, OffsetTile<.reuse>, ExpectedTile<.reuse>, DesiredTile<.reuse>, [RegSrc], ->DstTile<Size>
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|------|----------|
| **Col** | Tile 中数据和 offset 的列数，通过 `LB0` 传入。 | 否 |
| **Row** | Tile 中数据和 offset 的行数，通过 `LB1` 传入。 | 是，默认为 1 |
| **DataType** | 原子比较交换的数据类型/格式。 | 否 |
| **RegSrc** | 输入全局寄存器 GGPR，保存基地址 `baseAddress`。 | 否 |
| **OffsetTile** | 输入 Tile，保存基于 `baseAddress` 的 byte offset。 | 否 |
| **ExpectedTile** | 输入 Tile，保存每个元素的期望旧值。 | 否 |
| **DesiredTile** | 输入 Tile，保存比较成功时写入的新值。 | 否 |
| **DstTile** | 输出 Tile，保存每个地址上的旧值。 | 否 |
| **Size** | 输出 Tile 大小，必须等于 `Row * Col * sizeof(DataType)`。 | 否 |

`OffsetTile` 中 offset 的位宽由写入该 Tile 时使用的元素位宽决定，规范形式
支持 `u16`、`u32` 和 `u64`。

## 编码格式

该 TileOp 编码为以下指令：

- [BSTART.MGATHER.CAS](../../blockIntro/tma_block/header.md) `DataType`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` *（`Col`）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` *（`Row`）*
- [B.IOT](../../header/B.IOT.md) `OffsetTile<.reuse>, ExpectedTile<.reuse>, DesiredTile<.reuse>, last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

操作数角色固定为：

- 输入：`OffsetTile`、`ExpectedTile`、`DesiredTile`
- 输出：`DstTile`（旧值）
- 标量基址：第一个 `B.IOR` 输入寄存器

## 执行模型

```c
void MGATHER_CAS(Tile dst, Scalar base, Tile offset, Tile expected, Tile desired) {
  for (int i = 0; i < Row; ++i) {
    for (int j = 0; j < Col; ++j) {
      uintptr_t addr = base + offset[i][j];
      DataType old = atomic_load(addr);
      if (old == expected[i][j]) {
        atomic_store(addr, desired[i][j]);
      }
      dst[i][j] = old;
    }
  }
}
```

## 注意事项

- 每个有效元素执行一次比较交换；旧值总是写入 `DstTile`。
- 如果多个有效元素映射到同一地址，元素间顺序由实现定义，但每个元素自身的比较交换必须保持原子性。
- `Size` 必须是 `Col * sizeof(DataType)` 的整数倍。
- 该操作属于 TMA function 8；function 9..31 保留。
