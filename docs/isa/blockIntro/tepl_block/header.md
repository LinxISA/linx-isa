# headerDefinition

The header of the template data block needs to define which data operation operation to perform, the size of the input data and the Tile register of input/output and other information.

## Assembly format

```asm
TileOp <LB0:arg0, LB1:arg1, LB2:arg2, DataType>, SrcTile0<.reuse>, ..., SrcTile7<.reuse>, [BGetList],  
                                               ->DstTile0<TileSize0>, ..., DstTile3<TileSize3>, [BSetList]
```

Each parameter is explained as follows:

| Parameters | Description | Optional or not |
|------|------|---------|
| **TileOp** | Specify the specific operation of data transfer, optional: TADD, TANDS, etc. | No |
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

## Encoding method

A complete data transfer block instructionheader needs to be split into the following multiple instructions for encoding, including:

- `BSTART.TEPL TileOp, DataType`
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

Among them, the encoding format of the BSTART.TEPL instruction is as follows:

![BSTART.TEPL](../../../figs/bitfield/svg/BlockHeader_32bit/BSTART.TEPL.svg)

Among them, the mode and function fields are used to encode specific TileOp information. The encoding method is as follows:

### **Tile-Tile element-by-element operation**| Mode | Function | Operation | Description |
|------|----------|--------|------|
| 0 | 0 | [TADD](../../header/tileblock/TADD.md) | Element-wise addition of two Tiles |
| 0 | 1 | [TSUB](../../header/tileblock/TSUB.md) | Element-wise subtraction of two Tiles |
| 0 | 2 | [TMUL](../../header/tileblock/TMUL.md) | Element-wise multiplication of two Tiles |
| 0 | 3 | [TDIV](../../header/tileblock/TDIV.md) | Element-wise division of two Tiles |
| 0 | 4 | [TREM](../../header/tileblock/TREM.md) | Element-wise remainder of two Tiles, the remainder sign is the same as the divisor |
| 0 | 5 | [TFMOD](../../header/tileblock/TFMOD.md) | Element-wise remainder of two Tiles, the remainder sign is the same as the dividend |
| 0 | 6 | [TAND](../../header/tileblock/TAND.md) | Element-wise bitwise AND of two Tiles |
| 0 | 7 | [TOR](../../header/tileblock/TOR.md) | Element-wise bitwise OR of two Tiles |
| 0 | 8 | [TXOR](../../header/tileblock/TXOR.md) | Element-wise bitwise XOR of two Tiles |
| 0 | 9 | [TSHL](../../header/tileblock/TSHL.md) | Element-wise left shift of two Tiles |
| 0 | 10 | [TSHR](../../header/tileblock/TSHR.md) | Element-wise right shift of two Tiles |
| 0 | 11 | [TMAX](../../header/tileblock/TMAX.md) | Element-wise maximum value of two Tiles |
| 0 | 12 | [TMIN](../../header/tileblock/TMIN.md) | Element-wise minimum value of two Tiles |
| 0 | 13 | [TCMP](../../header/tileblock/TCMP.md) | Compares two Tiles and writes a packed predicate mask |
| 0 | 14 | [TPRELU](../../header/tileblock/TPRELU.md) | Element-wise parameterized ReLU with element-wise slope Tile |
| 0 | 15 | [TABS](../../header/tileblock/TABS.md) | Element-wise absolute value of Tile |
| 0 | 16 | [TNOT](../../header/tileblock/TNOT.md) | Element-wise bitwise inversion of Tile |
| 0 | 17 | [TNEG](../../header/tileblock/TNEG.md) | Element-wise negation of Tile |
| 0 | 18 | [TEXP](../../header/tileblock/TEXP.md) | Element-wise exponential operation |
| 0 | 19 | [TLOG](../../header/tileblock/TLOG.md) | Element-wise natural logarithm of Tile |
| 0 | 20 | [TRECIP](../../header/tileblock/TRECIP.md) | Element-wise reciprocal of Tile |
| 0 | 21 | [TSQRT](../../header/tileblock/TSQRT.md) | Element-wise square root |
| 0 | 22 | [TRSQRT](../../header/tileblock/TRSQRT.md) | Element-wise reciprocal square root |
| 0 | 23 | [TRELU](../../header/tileblock/TRELU.md) | Element-wise ReLU of Tile || 0 | 24 | [TADDC](../../header/tileblock/TADDC.md) | Ternary element-wise addition: dst = src0 + src1 + src2 |
| 0 | 25 | [TSUBC](../../header/tileblock/TSUBC.md) | Ternary element-wise subtraction: dst = src0 - src1 + src2 |
| 0 | 26 | [TSEL](../../header/tileblock/TSEL.md) | Select between two Tiles using a masked Tile (element-wise selection) |
| 0 | 27 | [TCVT](../../header/tileblock/TCVT.md) | Element-by-element data format conversion of Tile. |
| 0 | 28-31 | - | Reserved |

### **Tile element-by-element and scalar operations**| Mode | Function | Operation | Description |
|------|----------|--------|------|
| 1 | 0 | [TADDS](../../header/tileblock/TADDS.md) | Element-wise addition of Tile and scalar |
| 1 | 1 | [TSUBS](../../header/tileblock/TSUBS.md) | Subtract a scalar from the Tile element by element |
| 1 | 2 | [TMULS](../../header/tileblock/TMULS.md) | Element-wise multiplication of Tile and scalar |
| 1 | 3 | [TDIVS](../../header/tileblock/TDIVS.md) | Element-wise division with scalar (Tile/scalar or scalar/Tile) |
| 1 | 4 | [TREMS](../../header/tileblock/TREMS.md) | Element-wise remainder with scalar: remainder(src, scalar) |
| 1 | 5 | [TFMODS](../../header/tileblock/TFMODS.md) | Element-wise remainder with scalar: fmod(src, scalar) |
| 1 | 6 | [TANDS](../../header/tileblock/TANDS.md) | Element-wise bitwise AND of Tile and scalar |
| 1 | 7 | [TORS](../../header/tileblock/TORS.md) | Element-wise bitwise OR of Tile and scalar |
| 1 | 8 | [TXORS](../../header/tileblock/TXORS.md) | Element-wise bitwise XOR of Tile and scalar |
| 1 | 9 | [TSHLS](../../header/tileblock/TSHLS.md) | Tile moves left element by element according to scalar |
| 1 | 10 | [TSHRS](../../header/tileblock/TSHRS.md) | Tile moves right element by element according to scalar |
| 1 | 11 | [TMAXS](../../header/tileblock/TMAXS.md) | Element-wise maximum value of Tile and scalar: max(src, scalar) |
| 1 | 12 | [TMINS](../../header/tileblock/TMINS.md) | Element-wise minimum value of Tile and scalar |
| 1 | 13 | [TCMPS](../../header/tileblock/TCMPS.md) | Compare Tile with scalar element by element |
| 1 | 14 | [TLRELU](../../header/tileblock/TLRELU.md) | LeakyReLU with scalar slope |
| 1 | 15-23 | - | Reserved code |
| 1 | 24 | [TADDSC](../../header/tileblock/TADDSC.md) | With scalar fusion element-wise addition operation: dst = src0 + scalar + src1 |
| 1 | 25 | [TSUBSC](../../header/tileblock/TSUBSC.md) | With scalar fused element-wise subtraction operation: dst = src0 - scalar + src1 |
| 1 | 26 | [SELS](../../header/tileblock/TSELS.md) | Use mask Tile to select between source Tile and scalar (source Tile element-wise selection) || 1 | 27 | [TEXPANDS](../../header/tileblock/TEXPANDS.md) | Broadcast scalar to the target Tile |
| 1 | 28-31 | - | Reserved code |

### **Axis-wise reduction/broadcast operation**| Mode | Function | Operation | Description |
|------|----------|------------------|------|
| 2 | 0 | [TROWSUM](../../header/tileblock/TROWSUM.md) | Reduce each row by summing the columns |
| 2 | 1 | [TROWMAX](../../header/tileblock/TROWMAX.md) | Reduce each row by taking the maximum value between columns |
| 2 | 2 | [TROWMIN](../../header/tileblock/TROWMIN.md) | Reduce each row by taking the minimum value between columns |
| 2 | 3 | [TROWPROD](../../header/tileblock/TROWPROD.md) | Reduce each row by product across columns |
| 2 | 4 | [TROWEXPAND](../../header/tileblock/TROWEXPAND.md) | Broadcast the first element of each source row into the target row |
| 2 | 5 | [TROWEXPANDADD](../../header/tileblock/TROWEXPANDADD.md) | Line broadcast addition: add one per line scalarvector |
| 2 | 6 | [TROWEXPANDSUB](../../header/tileblock/TROWEXPANDSUB.md) | Row broadcast subtraction: subtract one per row from src0 scalarvectorsrc1 |
| 2 | 7 | [TROWEXPANDMUL](../../header/tileblock/TROWEXPANDMUL.md) | Row broadcast multiplication: multiply each row of src0 by one per row scalarvectorsrc1 |
| 2 | 8 | [TROWEXPANDDIV](../../header/tileblock/TROWEXPANDDIV.md) | Row broadcast division: divide each row of src0 by one per row scalarvectorsrc1 |
| 2 | 9 | [TROWEXPANDMAX](../../header/tileblock/TROWEXPANDMAX.md) | Line broadcast maximum value: take the maximum value with each line scalarvector |
| 2 | 10 | [TROWEXPANDMIN](../../header/tileblock/TROWEXPANDMIN.md) | Row broadcast minimum value: take the minimum value with each row scalarvector |
| 2 | 11 | [TROWEXPANDEXPDIF](../../header/tileblock/TROWEXPANDEXPDIF.md) | Row exponential difference operation: calculate exp(src0 - src1), where src1 is each row scalar |
| 2 | 12-15 | - | Reserved coding |
| 2 | 16 | [TCOLSUM](../../header/tileblock/TCOLSUM.md) | Reduce each column by summing the rows |
| 2 | 17 | [TCOLMAX](../../header/tileblock/TCOLMAX.md) | Reduce each column by taking the maximum value between rows |
| 2 | 18 | [TCOLMIN](../../header/tileblock/TCOLMIN.md) | Reduce each column by taking the minimum value between rows |
| 2 | 19 | [TCOLPROD](../../header/tileblock/TCOLPROD.md) | Reduce each column by product across rows |
| 2 | 20 | [TCOLEXPAND](../../header/tileblock/TCOLEXPAND.md) | Broadcast the first element of each source column to the target column || 2 | 21 | [TCOLEXPANDADD](../../header/tileblock/TCOLEXPANDADD.md) | Column broadcast addition: add one per column scalarvector |
| 2 | 22 | [TCOLEXPANDSUB](../../header/tileblock/TCOLEXPANDSUB.md) | Column broadcast subtraction: subtract one per column from each column of src0 scalarvectorsrc1 |
| 2 | 23 | [TCOLEXPANDMUL](../../header/tileblock/TCOLEXPANDMUL.md) | Column broadcast multiplication: multiply each column of src0 by one per column scalarvectorsrc1 |
| 2 | 24 | [TCOLEXPANDDIV](../../header/tileblock/TCOLEXPANDDIV.md) | Column broadcast division: divide each column of src0 by one per column scalarvectorsrc1 |
| 2 | 25 | [TCOLEXPANDMAX](../../header/tileblock/TCOLEXPANDMAX.md) | Column broadcast maximum value: take the maximum value with each column scalarvector |
| 2 | 26 | [TCOLEXPANDMIN](../../header/tileblock/TCOLEXPANDMIN.md) | Column broadcast minimum value: take the minimum value with each column scalarvector |
| 2 | 27 | [TCOLEXPANDEXPDIF](../../header/tileblock/TCOLEXPANDEXPDIF.md) | Column exponential difference operation: calculate exp(src0 - src1), where src1 is each column scalar |
| 2 | 28-31 | - | Reserved coding |

### **Complex operation**

| Mode | Function | Operation | Description |
|------|----------|------------------|------|
| 3 | 0-7 | - | Reserved code |
| 3 | 8 | [THISTOGRAM](../../header/templateblock/THISTOGRAM.md) | Cumulative histogram statistics command |
| 3 | 9-29 | - | Reserved coding |
| 3 | 30 | [ESAVE](../../header/templateblock/ESAVE.md) | exception save block, used to save the block state of the Tile block where exception occurs |
| 3 | 31 | [ERCOV](../../header/templateblock/ERCOV.md) | exception recovery block, used to restore the intra-block state of the Tile block where exception occurred |

The DataType field is encoded as follows:| Encoding | DataType | Encoding | DataType | Encoding | DataType | Encoding | Data |
|------|----------|------|-----------|------|-----------|------|-----------|
| 0 | FP64 | 8 | e5m2 | 16 | S64 | 24 | U64 |
| 1 | FP32 | 9 | e3m2 | 17 | S32 | 25 | U32 |
| 2 | TF32 | 10 | e2m3 | 18 | S16 | 26 | U16 |
| 3 | HF32 | 11 | e2m1x2 | 19 | S8 | 27 | U8 |
| 4 | FP16 | 12 | e1m2x2 | 20 | S4x2 | 28 | U4x2 |
| 5 | BF16 | 13 | e8m0 | 21 | reserve | 29 | reserve |
| 6 | HiF8 | 14 | HiF4x2 | 22 | reserve | 30 | reserve |
| 7 | e4m3 | 15 | reserve | 23 | reserve | 31 | invalid |