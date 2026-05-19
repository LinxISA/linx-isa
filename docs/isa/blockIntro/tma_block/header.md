# headerDefinition

The header of the data transfer block needs to define which data transfer operation is performed, the size of the input data and the Tile register of input/output and other information. The storage layout is also supported during the data transfer process.

## Assembly format

```asm
TileOp <LB0:arg0, LB1:arg1, LB2:arg2, DataType>, SrcTile0<.reuse>, ..., SrcTile7<.reuse>, DepSrc, [BGetList],  
                                     ->DstTile0<TileSize0>, ..., DstTile3<TileSize3>, [BSetList], DepDst
```

Each parameter is explained as follows:

| Parameters | Description | Optional or not |
|------|------|---------|
| **TileOp** | Specify the specific operation of data transfer, optional: TLOAD, TSTORE, etc. | No |
| **LB0** | Row or column parameters of input data. For details, see the introduction of specific instructions. It can be set through the arg0 (`全局寄存器`, `立即数` or `全局寄存器加立即数`) parameter. | Yes, default is 1 |
| **LB1** | Row or column parameters of input data. For details, see the introduction of specific instructions. It can be set through the arg1 (`全局寄存器`, `立即数` or `全局寄存器加立即数`) parameter. | Yes, default is 1 |
| **LB2** | Row or column parameters of input data. For details, see the introduction of specific instructions. It can be set through the arg2 (`全局寄存器`, `立即数` or `全局寄存器加立即数`) parameter. | Yes, default is 1 |
| **DataType** | The data format of the input element, including FP32, FP16, S16, etc. | Yes |
| **SrcTile0, ..., SrcTile7** | Indicate up to 8 input Tile registers respectively. | Yes |
| **reuse** | This flag needs to be added when the corresponding input Tile register is not allowed to be released after the execution of this instruction. If there is no such mark, it means that the hardware is allowed to release this register. | Yes |
| **DstTile0, ..., DstTile3** | Indicate up to 4 output Tile register types respectively | Optional T, U, M, N. | Yes |
| **TileSize0, ..., TileSize3** | Indicates the space size of each output Tile register respectively. The parameter can be passed through a `立即数` or `全局寄存器`. | Depends on DstTile |
| **[BGetList]** | Global register [GGPR](../../register/common/ggpr.md) input list. | Yes |
| **[BSetList]** | Global register [GGPR](../../register/common/ggpr.md) output list. | Yes |
| **DepSrc** | Indicates the dependence of this block instruction on the previous block instruction output to D. | Yes |
| **DepDst** | Indicates the barrier of this block instruction to the block instruction that references this identifier in subsequent sequences. | Yes |

## Encoding method

A complete data transfer block instructionheader needs to be split into the following multiple instructions for encoding, including:

- `BSTART.TMA TileOp, DataType`
- [B.DATR](../../header/B.DATR.md) `Layout, PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, ->DstTile0<TileSize0>`
-...
- [B.IOT](../../header/B.IOT.md) `SrcTile6<.reuse>, SrcTile7<.reuse>, last, ->DstTile3<TileSize3>`
- [B.IOR](../../header/B.IOR.md) `RegSrc0, RegSrc1, RegSrc2, ->RegDst0`
-...
- [B.IOR](../../header/B.IOR.md) `RegSrc9, RegSrc10, RegSrc11, ->RegDst4`
- [B.IOD](../../header/B.IOD.md) `DepSrc, ->DepDst`

Among them, the encoding format of the BSTART.TMA instruction is as follows:![BSTART.TMA](../../../figs/bitfield/svg/BlockHeader_32bit/BSTART.TMA.svg)

Among them, the function field is used to encode specific TileOp information. The encoding method is as follows:

| function | TileOp | description |
|------|-------|---------|
| 0 | [TLOAD](../../header/tileblock/TLOAD.md) | Load data from memory into Tile register |
| 1 | [TSTORE](../../header/tileblock/TSTORE.md) | Move Tile register data to memory |
| 2 | [TMOV](../../header/tileblock/TMOV.md) | Data movement/copying between Tile registers, supporting storage layout (fractal) transformation |
| 3 | - | Reserved |
| 4 | [MGATHER](../../header/tileblock/MGATHER.md) | Gather data in discrete memory space into Tile registers. |
| 5 | [MSCATTER](../../header/tileblock/MSCATTER.md) | Store the data in the Tile register into discrete memory space.  |
| 6-31 | Temporarily reserved |

The DataType field is encoded as follows:

| Encoding | DataType | Encoding | DataType | Encoding | DataType | Encoding | Data |
|------|----------|------|-----------|------|-----------|------|-----------|
| 0 | FP64 | 8 | e5m2 | 16 | S64 | 24 | U64 |
| 1 | FP32 | 9 | e3m2 | 17 | S32 | 25 | U32 |
| 2 | TF32 | 10 | e2m3 | 18 | S16 | 26 | U16 |
| 3 | HF32 | 11 | e2m1x2 | 19 | S8 | 27 | U8 |
| 4 | FP16 | 12 | e1m2x2 | 20 | S4x2 | 28 | U4x2 |
| 5 | BF16 | 13 | e8m0 | 21 | reserve | 29 | reserve |
| 6 | HiF8 | 14 | HiF4x2 | 22 | reserve | 30 | reserve |
| 7 | e4m3 | 15 | reserve | 23 | reserve | 31 | invalid |