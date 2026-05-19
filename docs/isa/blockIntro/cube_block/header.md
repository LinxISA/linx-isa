# headerDefinition

The header of the matrix data block needs to define which type of matrix operation operation is performed, the size of the input matrix and the Tile register of input/output and other information.

## Assembly format

```asm
TileOp <LB0:arg0, LB1:arg1, LB2:arg2, DataType>, SrcTile0<.reuse>, ..., SrcTile7<.reuse>, DepSrc, 
                                     ->DstTile0<TileSize0>, ..., DstTile3<TileSize3>, DepDst
```

Each parameter is explained as follows:

| Parameters | Description | Optional or not |
|------|------|---------|
| **TileOp** | Specify the specific operation of matrix operation, optional: TMATMUL, ACCCVT, etc. | No |
| **LB0** | Enter the row or column parameters of the matrix. For details, see the introduction of specific instructions. arg0 can be set by (`全局寄存器`, `立即数` or `全局寄存器加立即数`) parameters. | Yes, default is 1 |
| **LB1** | Enter the row or column parameters of the matrix. For details, see the introduction of specific instructions. arg1 can be set by (`全局寄存器`, `立即数` or `全局寄存器加立即数`) parameters. | Yes, default is 1 |
| **LB2** | Enter the row or column parameters of the matrix. For details, see the introduction of specific instructions. arg2 can be set by (`全局寄存器`, `立即数` or `全局寄存器加立即数`) parameters. | Yes, default is 1 |
| **DataType** | The data format of the input element, including FP32, FP16, S16, etc. | Yes |
| **SrcTile0, ..., SrcTile7** | Indicate up to 8 input Tile registers respectively. | Yes |
| **reuse** | This flag needs to be added when the corresponding input Tile register is not allowed to be released after the execution of this instruction. If there is no such mark, it means that the hardware is allowed to release this register. | Yes |
| **DstTile0, ..., DstTile3** | Indicate up to 4 output Tile register types respectively | Optional T, U, M, N or ACC. | Yes |
| **TileSize0, ..., TileSize3** | Indicates the space size of each output Tile register respectively. The parameter can be passed through a `立即数` or `全局寄存器`. | Depends on DstTile |
| **DepSrc** | Indicates the dependence of this block instruction on the previous block instruction output to D. | Yes |
| **DepDst** | Indicates the barrier of this block instruction to the block instruction that references this identifier in subsequent sequences. | Yes |

## Encoding method

A complete matrix data block instructionheader needs to be split into the following instructions for encoding, including:

- BSTART.CUBE TileOp, DataType
- [B.DATR](../../header/B.DATR.md) Layout.{canon, normal}, DataType
- [B.DIM](../../header/B.DIM.md) reg, imm, ->LB0
- [B.DIM](../../header/B.DIM.md) reg, imm, ->LB1
- [B.DIM](../../header/B.DIM.md) reg, imm, ->LB2
- [B.IOT](../../header/B.IOT.md) SrcTile0<.reuse>, SrcTile1<.reuse>, ->DstTile0<TileSize0>
-...
- [B.IOT](../../header/B.IOT.md) SrcTile6<.reuse>, SrcTile7<.reuse>, last, ->DstTile3<TileSize3>
- [B.IOD](../../header/B.IOD.md) DepSrc, ->DepDst

Among them, the encoding format of the BSTART.CUBE instruction is as follows:

![BSTART.CUBE](../../../figs/bitfield/svg/BlockHeader_32bit/BSTART.CUBE.svg)Among them, the function field is used to encode specific matrix operations/FIXPIPE instructions. The encoding method is as follows:

| Mode | Function | Operation |
|------|----------|------------------|
| 0 | 0 | [TMATMUL](../../header/tileblock/TMATMUL.md) |
| 0 | 1 | [TMATMUL.BIAS](../../header/tileblock/TMATMUL.BIAS.md) |
| 0 | 2 | [TMATMUL.ACC](../../header/tileblock/TMATMUL.ACC.md) |
| 0 | 3 | Reserved encoding |
| 0 | 4 | [TMATMULMX](../../header/tileblock/TMATMULMX.md) |
| 0 | 5 | [TMATMULMX.BIAS](../../header/tileblock/TMATMULMX.BIAS.md) |
| 0 | 6 | [TMATMULMX.ACC](../../header/tileblock/TMATMULMX.ACC.md) |
| 0 | 7 | Reserved encoding |
| 0 | 8 | [ACCCVT](../../header/tileblock/ACCCVT.md) |
| 0 | 9-15 | Reserved encoding |
| 0 | 16 | [TGEMV](../../header/tileblock/TGEMV.md) |
| 0 | 17 | [TGEMV.BIAS](../../header/tileblock/TGEMV.BIAS.md) |
| 0 | 18 | [TGEMV.ACC](../../header/tileblock/TGEMV.ACC.md) |
| 0 | 19 | Reserved encoding |
| 0 | 20 | [TGEMVMX](../../header/tileblock/TGEMVMX.md) |
| 0 | 21 | [TGEMVMX.BIAS](../../header/tileblock/TGEMVMX.BIAS.md) |
| 0 | 22 | [TGEMVMX.ACC](../../header/tileblock/TGEMVMX.ACC.md) |
| 0 | 23-31 | Reserved encoding |

The DataType field is encoded as follows:| Coding | data type | Coding | data type | Coding | data type | Coding | data type |
|------|----------|------|----------|------|----------|------|----------|
| 0 | FP64 | 8 | E5M2 | 16 | S64 | 24 | U64 |
| 1 | FP32 | 9 | E3M2 | 17 | S32 | 25 | U32 |
| 2 | TF32 | 10 | E2M3 | 18 | S16 | 26 | U16 |
| 3 | HF32 | 11 | E2M1x2 | 19 | S8 | 27 | U8 |
| 4 | FP16 | 12 | E1M2x2 | 20 | S4x2 | 28 | U4x2 |
| 5 | BF16 | 13 | E8M0 | 21 | reserve | 29 | reserve |
| 6 | HiF8 | 14 | HiF4x2 | 22 | reserve | 30 | reserve |
| 7 | E4M3 | 15 | reserve | 23 | reserve | 31 | invalid |