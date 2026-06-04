# TileInfo

Tile 元数据寄存器（Tile Information Register），简称 TileInfo，是硬件内部维护的一组 **banked 寄存器族（SSR family）**，每个 Tile 寄存器对应一个独立的 TileInfo 实例，用于记录该 Tile 的元数据快照。

TileInfo **不对软件可见**——软件不可通过 SSRGET/SSRSET 等指令读写。其生命周期完全由硬件管理：

- **写入**：当块指令通过 [B.IOT](../../header/B.IOT.md) 将数据输出到一个 Tile 寄存器时，硬件自动将相关参数（维度、数据类型、布局、容量等）写入该 Tile 对应的 TileInfo。
- **读取**：当后序块指令以该 Tile 作为输入时，硬件从对应的 TileInfo 中获取元数据，无需软件在指令中重复描述输入 Tile 的参数。

## 寄存器位域

每个 TileInfo 实例为 64-bit，位域定义如下：

| 位域 | 位宽 | 说明 |
|------|------|------|
| `vld` | 1 | Tile 是否已分配/有效。`0` = 无效（未分配或已释放），`1` = 已分配/有效。 |
| `p` | 1 | PredicateTile 标记。`0` = 普通 Tile，`1` = 谓词 Tile。 |
| `Layout` | 3 | Tile 数据的存储布局（分形）类型，编码见下表。 |
| `DataType` | 6 | Tile 中元素的数据类型，编码同 [BSTART](../../header/BSTART.md) 的 DataType 字段。 |
| `size` | 4 | Tile 容量编码，编码映射同 [B.IOT](../../header/B.IOT.md) 中目的寄存器容量编码。 |
| — | 1 | 保留。 |
| `validCol` | 16 | Tile 中有效数据的列数。`validCol ≤ Col`。 |
| `validRow` | 16 | Tile 中有效数据的行数。`validRow ≤ Row`，其中 `Row = TileSize / (Col × sizeof(DataType))`。 |
| `Col` | 16 | Tile 中数据的总列数（含 Padding 列）。 |

## Layout 编码

| Layout | 布局/分形 | 说明 |
|--------|----------|------|
| 0 | ND | 行优先（Row-Major） |
| 1 | Zz | 大 Z 小 z |
| 2 | Zn | 大 Z 小 n |
| 3 | DN | 列优先（Col-Major） |
| 4 | Nz | 大 N 小 Z |
| 5 | Nn | 大 N 小 N |
| 6~7 | — | 预留 |

## 设计说明

TileInfo 不是单个 64-bit SSR，而是一组按 Tile 编号索引的 **SSR family**（banked 视图）。每个 Tile 寄存器（共 64 个）拥有独立的 TileInfo 实例，64 个 Tile 的完整元数据无法装入单个窄寄存器中。

TileInfo 的引入使得 TileOp 指令的 LB 参数语义得以简化：输入 Tile 的维度、数据类型、布局等信息由硬件从 TileInfo 自动获取，指令仅需通过 LB 描述**输出 Tile** 的参数。

## 备注

TileInfo 为硬件内部寄存器，**不分配 SSRID，软件不可访问**。Tile 元数据由硬件在 B.IOT 分配/写入 Tile 时自动维护。
