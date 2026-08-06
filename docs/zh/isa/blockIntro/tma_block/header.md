# 块头定义

数据搬运块的块头需要定义执行哪种数据搬运操作、输入数据的尺寸和输入输出的Tile寄存器等信息。数据搬运过程中同时支持改变存储布局。

## 汇编格式

```asm
TileOp <LB0:arg0, LB1:arg1, LB2:arg2, DataType>, SrcTile0<.reuse>, ..., SrcTile7<.reuse>, DepSrc0, DepSrc1, DepSrc2, [BGetList],  
                                     ->DstTile0<TileSize0>, ..., DstTile3<TileSize3>, [BSetList], DepDst
```

各参数说明如下：

| 参数 | 说明 | 是否可选 |
|------|------|---------|
| **TileOp** | 指定数据搬运的具体操作，可选：TLOAD, TSTORE等 | 否  |
| **LB0** | 输入数据的行或列参数，具体见特定指令介绍。可以通过arg0（`全局寄存器`、`立即数`或`全局寄存器加立即数`）参数设置。 | 是，默认为1 |
| **LB1** | 输入数据的行或列参数，具体见特定指令介绍。可以通过arg1（`全局寄存器`、`立即数`或`全局寄存器加立即数`）参数设置。 | 是，默认为1 |
| **LB2** | 输入数据的行或列参数，具体见特定指令介绍。可以通过arg2（`全局寄存器`、`立即数`或`全局寄存器加立即数`）参数设置。 | 是，默认为1 |
| **DataType** | 输入元素的数据格式，包括FP32, FP16, S16等 | 是 |
| **SrcTile0, ..., SrcTile7** | 分别指示最多8个输入的Tile寄存器。 | 是 |
| **reuse** | 当本指令执行结束后相应的输入Tile寄存器不允许被释放则需要增加该标识。如无此标识，则表示允许硬件释放本寄存器。 | 是 |
| **DstTile0, ..., DstTile3** | 分别指示最多4个输出Tile寄存器类型 | 可选T, U, M, N。 | 是 |
| **TileSize0, ..., TileSize3** | 分别指示每个输出Tile寄存器的空间大小，可以通过一个 `立即数`或者`全局寄存器`传参。 | 取决于DstTile |
| **[BGetList]** | 全局寄存器[GGPR](../../register/common/ggpr.md)输入列表。 | 是 |
| **[BSetList]** | 全局寄存器[GGPR](../../register/common/ggpr.md)输出列表。 | 是 |
| **DepSrc0, DepSrc1, DepSrc2** | 表示本块指令最多显式记录 3 个前序 `D` 依赖槽位。 | 是 |
| **DepDst** | 表示本块指令对后序引用该标识的块指令的屏障。 | 是 |

## 编码方式

一条完整数据搬运块指令块头需要拆分成以下多条指令进行编码，其中包括：

- 命名块头：`BSTART.TLOAD DataType`、`BSTART.TSTORE DataType`、`BSTART.TMOV DataType`、
  `BSTART.TPREFETCH DataType`、`BSTART.MGATHER DataType`、`BSTART.MSCATTER DataType`、
  `BSTART.MGATHER.MASK DataType`、`BSTART.MSCATTER.MASK DataType`、
  `BSTART.MGATHER.CAS DataType`、
  `BSTART.GMOV DataType`
- [B.DATR](../../header/B.DATR.md) `Layout, PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, ->DstTile0<TileSize0>`
- ...
- [B.IOT](../../header/B.IOT.md) `SrcTile6<.reuse>, SrcTile7<.reuse>, last, ->DstTile3<TileSize3>`
- [B.IOR](../../header/B.IOR.md) `RegSrc0, RegSrc1, RegSrc2, ->RegDst0`
- ...
- [B.IOR](../../header/B.IOR.md) `RegSrc9, RegSrc10, RegSrc11, ->RegDst4`

其中，TLSU 命名块头共享同一个相邻编码族；`function` 字段选择具体 TileOp。
旧的泛化文本汇编形式已退役，活动汇编必须使用命名块头。
TPREFETCH 与 TLOAD 相邻编码，是没有目标 Tile 的预取形式。

TLSU 编码族的格式如下（图文件沿用历史名称）：

![TLSU 编码族（历史图文件名）](../../../figs/bitfield/svg/BlockHeader_32bit/BSTART.TMA.svg)

其中，function字段用于编码具体的TileOp信息。编码方式如下：

| function | TileOp |  说明 |
|------|-------|---------|
| 0 | [TLOAD](../../header/tileblock/TLOAD.md)   | 从内存加载数据到Tile寄存器中 |
| 1 | [TSTORE](../../header/tileblock/TSTORE.md) | 把Tile寄存器数据搬运到内存中 |
| 2 | [TMOV](../../header/tileblock/TMOV.md)     | Tile寄存器之间的数据移动/复制，支持存储布局（分形）变换 |
| 3 | [TPREFETCH](../../header/tileblock/TPREFETCH.md) | 与 TLOAD 使用相同地址/尺寸描述，但不写目标 Tile；用于预取 |
| 4 | [MGATHER](../../header/tileblock/MGATHER.md) | 将离散的内存空间中的数据聚集到Tile寄存器中。 |
| 5 | [MSCATTER](../../header/tileblock/MSCATTER.md) | 将Tile寄存器中的数据存储到离散的内存空间。  |
| 6 | `BSTART.MGATHER.MASK` | 带掩码的离散内存聚集；关闭的元素不产生访存效果 |
| 7 | `BSTART.MSCATTER.MASK` | 带掩码的离散内存散写；关闭的元素不产生访存效果 |
| 8 | `BSTART.MGATHER.CAS` | 每个活动元素执行一次原子读-改-写 compare-and-swap |
| 9 | [TMOV](../../header/tileblock/TMOV.md) Local-to-Shared insert | 使用 `C.B.IOS` 和 Local 源 `B.IOT` |
| 10 | [TMOV](../../header/tileblock/TMOV.md) Local-to-Shared publish | 使用 `C.B.IOS` 和 Local 源 `B.IOT` |
| 11 | [TMOV](../../header/tileblock/TMOV.md) Shared-to-Local broadcast | 使用 `C.B.IOS` 和 Local 目标 `B.IOT` |
| 12 | [TMOV](../../header/tileblock/TMOV.md) Shared-to-Local extract | 使用 `C.B.IOS` 和 Local 目标 `B.IOT` |
| 13 | `BSTART.GMOV` | Core4 协同全局内存搬运 |
| 14 | `TSTORE.SPART` | 使用 `C.B.IOS` 和 `B.IOR` 的 Shared 分区存储 |
| 15-31 | 保留 | 非法 |

DataType字段编码方式如下：

| 编码 | DataType | 编码 | DataType  | 编码 | DataType  | 编码 | Data  |
|------|----------|------|-----------|------|-----------|------|-----------|
| 0    | FP64     | 8    | e5m2      | 16   | S64       | 24   | U64       |
| 1    | FP32     | 9    | e3m2      | 17   | S32       | 25   | U32       |
| 2    | TF32     | 10   | e2m3      | 18   | S16       | 26   | U16       |
| 3    | HF32     | 11   | e2m1x2    | 19   | S8        | 27   | U8        |
| 4    | FP16     | 12   | e1m2x2    | 20   | S4x2      | 28   | U4x2      |
| 5    | BF16     | 13   | e8m0      | 21   | reserve   | 29   | reserve   |
| 6    | HiF8     | 14   | HiF4x2    | 22   | reserve   | 30   | reserve   |
| 7    | e4m3     | 15   | reserve   | 23   | reserve   | 31   | invalid   |
