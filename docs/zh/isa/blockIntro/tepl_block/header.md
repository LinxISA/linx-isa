# 块头定义

模版数据块的块头需要定义执行哪种数据运算操作、输入数据的尺寸和输入输出的Tile寄存器等信息。

## 汇编格式

```asm
TileOp <LB0:arg0, LB1:arg1, LB2:arg2, DataType>, SrcTile0<.reuse>, ..., SrcTile7<.reuse>, [BGetList],  
                                               ->DstTile0<TileSize0>, ..., DstTile3<TileSize3>, [BSetList]
```

各参数说明如下：

| 参数 | 说明 | 是否可选 |
|------|------|---------|
| **TileOp** | 指定数据搬运的具体操作，可选：TADD, TANDS等 | 否  |
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

## 编码方式

一条完整数据搬运块指令块头需要拆分成以下多条指令进行编码，其中包括：

- `BSTART.TEPL TileOp, DataType`
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
- [B.IOD](../../header/B.IOD.md) `DepSrc, ->DepDst`

其中，BSTART.TEPL指令的编码格式如下：

![BSTART.TEPL](../../../figs/bitfield/svg/BlockHeader_32bit/BSTART.TEPL.svg)

其中，mode和function字段用于编码具体的TileOp信息。编码方式如下：

### **Tile-Tile逐元素操作**

| Mode | Function | 操作   | 说明 |
|------|----------|--------|------|
| 0    | 0        | [TADD](../../header/tileblock/TADD.md)   | 两个Tile的逐元素加法 |
| 0    | 1        | [TSUB](../../header/tileblock/TSUB.md)   | 两个Tile的逐元素减法 |
| 0    | 2        | [TMUL](../../header/tileblock/TMUL.md)   | 两个Tile的逐元素乘法 |
| 0    | 3        | [TDIV](../../header/tileblock/TDIV.md)   | 两个Tile的逐元素除法 |
| 0    | 4        | [TREM](../../header/tileblock/TREM.md)   | 两个Tile的逐元素余数，余数符号与除数相同 |
| 0    | 5        | [TFMOD](../../header/tileblock/TFMOD.md)  | 两个Tile的逐元素余数，余数符号与被除数相同 |
| 0    | 6        | [TAND](../../header/tileblock/TAND.md)   | 两个Tile的逐元素按位与 |
| 0    | 7        | [TOR](../../header/tileblock/TOR.md)     | 两个Tile的逐元素按位或 |
| 0    | 8        | [TXOR](../../header/tileblock/TXOR.md)   | 两个Tile的逐元素按位异或 |
| 0    | 9        | [TSHL](../../header/tileblock/TSHL.md)   | 两个Tile的逐元素左移 |
| 0    | 10       | [TSHR](../../header/tileblock/TSHR.md)   | 两个Tile的逐元素右移 |
| 0    | 11       | [TMAX](../../header/tileblock/TMAX.md)   | 两个Tile的逐元素最大值 |
| 0    | 12       | [TMIN](../../header/tileblock/TMIN.md)   | 两个Tile的逐元素最小值 |
| 0    | 13       | [TCMP](../../header/tileblock/TCMP.md)   | 比较两个Tile并写入一个打包的谓词掩码 |
| 0    | 14       | [TPRELU](../../header/tileblock/TPRELU.md) | 带逐元素斜率Tile的逐元素参数化ReLU |
| 0    | 15       | [TABS](../../header/tileblock/TABS.md)   | Tile的逐元素绝对值 |
| 0    | 16       | [TNOT](../../header/tileblock/TNOT.md)   | Tile的逐元素按位取反 |
| 0    | 17       | [TNEG](../../header/tileblock/TNEG.md)   | Tile的逐元素取负 |
| 0    | 18       | [TEXP](../../header/tileblock/TEXP.md)   | 逐元素指数运算 |
| 0    | 19       | [TLOG](../../header/tileblock/TLOG.md)   | Tile的逐元素自然对数 |
| 0    | 20       | [TRECIP](../../header/tileblock/TRECIP.md) | Tile的逐元素倒数 |
| 0    | 21       | [TSQRT](../../header/tileblock/TSQRT.md)  | 逐元素平方根 |
| 0    | 22       | [TRSQRT](../../header/tileblock/TRSQRT.md) | 逐元素倒数平方根 |
| 0    | 23       | [TRELU](../../header/tileblock/TRELU.md)  | Tile的逐元素ReLU |
| 0    | 24       | [TADDC](../../header/tileblock/TADDC.md)  | 三元逐元素加法：dst = src0 + src1 + src2 |
| 0    | 25       | [TSUBC](../../header/tileblock/TSUBC.md)  | 三元逐元素减法：dst = src0 - src1 + src2 |
| 0    | 26       | [TSEL](../../header/tileblock/TSEL.md)   | 使用掩码Tile在两个Tile之间进行选择（逐元素选择） |
| 0    | 27       | [TCVT](../../header/tileblock/TCVT.md)   | Tile的逐元素数据格式转换。 |
| 0    | 28-31    | -      | 保留 |

### **Tile逐元素和标量操作**

| Mode | Function | 操作   | 说明 |
|------|----------|--------|------|
| 1    | 0        | [TADDS](../../header/tileblock/TADDS.md)  | Tile与标量的逐元素加法 |
| 1    | 1        | [TSUBS](../../header/tileblock/TSUBS.md)  | 从Tile中逐元素减去一个标量 |
| 1    | 2        | [TMULS](../../header/tileblock/TMULS.md)  | Tile与标量的逐元素乘法 |
| 1    | 3        | [TDIVS](../../header/tileblock/TDIVS.md)  | 与标量的逐元素除法（Tile/标量或标量/Tile） |
| 1    | 4        | [TREMS](../../header/tileblock/TREMS.md)  | 与标量的逐元素余数：remainder(src, scalar) |
| 1    | 5        | [TFMODS](../../header/tileblock/TFMODS.md) | 与标量的逐元素余数：fmod(src, scalar) |
| 1    | 6        | [TANDS](../../header/tileblock/TANDS.md)  | Tile与标量的逐元素按位与 |
| 1    | 7        | [TORS](../../header/tileblock/TORS.md)    | Tile与标量的逐元素按位或 |
| 1    | 8        | [TXORS](../../header/tileblock/TXORS.md)  | Tile与标量的逐元素按位异或 |
| 1    | 9        | [TSHLS](../../header/tileblock/TSHLS.md)  | Tile按标量逐元素左移 |
| 1    | 10       | [TSHRS](../../header/tileblock/TSHRS.md)  | Tile按标量逐元素右移 |
| 1    | 11       | [TMAXS](../../header/tileblock/TMAXS.md)  | Tile与标量的逐元素最大值：max(src, scalar) |
| 1    | 12       | [TMINS](../../header/tileblock/TMINS.md)  | Tile与标量的逐元素最小值 |
| 1    | 13       | [TCMPS](../../header/tileblock/TCMPS.md)  | 将Tile与标量逐元素比较 |
| 1    | 14       | [TLRELU](../../header/tileblock/TLRELU.md) | 带标量斜率的LeakyReLU |
| 1    | 15-23    | -      | 预留编码 |
| 1    | 24       | [TADDSC](../../header/tileblock/TADDSC.md) | 带标量融合逐元素加法运算：dst = src0 + scalar + src1 |
| 1    | 25       | [TSUBSC](../../header/tileblock/TSUBSC.md) | 带标量融合逐元素减法运算：dst = src0 - scalar + src1 |
| 1    | 26       | [SELS](../../header/tileblock/TSELS.md)  | 使用掩码Tile在源Tile和标量之间进行选择（源Tile逐元素选择） |
| 1    | 27       | [TEXPANDS](../../header/tileblock/TEXPANDS.md) | 将标量广播到目标Tile中 |
| 1    | 28-31    | -      | 预留编码 |

### **按轴归约/广播操作**

| Mode | Function | 操作             | 说明 |
|------|----------|------------------|------|
| 2    | 0        | [TROWSUM](../../header/tileblock/TROWSUM.md)          | 通过对列求和来归约每一行 |
| 2    | 1        | [TROWMAX](../../header/tileblock/TROWMAX.md)          | 通过取列间最大值来归约每一行 |
| 2    | 2        | [TROWMIN](../../header/tileblock/TROWMIN.md)          | 通过取列间最小值来归约每一行 |
| 2    | 3        | [TROWPROD](../../header/tileblock/TROWPROD.md)         | 通过跨列乘积来归约每一行 |
| 2    | 4        | [TROWEXPAND](../../header/tileblock/TROWEXPAND.md)       | 将每个源行的第一个元素广播到目标行中 |
| 2    | 5        | [TROWEXPANDADD](../../header/tileblock/TROWEXPANDADD.md)    | 行广播加法：加上一个每行标量向量 |
| 2    | 6        | [TROWEXPANDSUB](../../header/tileblock/TROWEXPANDSUB.md)    | 行广播减法：从src0的每一行中减去一个每行标量向量src1 |
| 2    | 7        | [TROWEXPANDMUL](../../header/tileblock/TROWEXPANDMUL.md)    | 行广播乘法：将src0的每一行乘以一个每行标量向量src1 |
| 2    | 8        | [TROWEXPANDDIV](../../header/tileblock/TROWEXPANDDIV.md)    | 行广播除法：将src0的每一行除以一个每行标量向量src1 |
| 2    | 9        | [TROWEXPANDMAX](../../header/tileblock/TROWEXPANDMAX.md)    | 行广播最大值：与每行标量向量取最大值 |
| 2    | 10       | [TROWEXPANDMIN](../../header/tileblock/TROWEXPANDMIN.md)    | 行广播最小值：与每行标量向量取最小值 |
| 2    | 11       | [TROWEXPANDEXPDIF](../../header/tileblock/TROWEXPANDEXPDIF.md) | 行指数差运算：计算exp(src0 - src1)，其中src1为每行标量 |
| 2    | 12-15    | -                | 预留编码 |
| 2    | 16       | [TCOLSUM](../../header/tileblock/TCOLSUM.md)          | 通过对行求和来归约每一列 |
| 2    | 17       | [TCOLMAX](../../header/tileblock/TCOLMAX.md)          | 通过取行间最大值来归约每一列 |
| 2    | 18       | [TCOLMIN](../../header/tileblock/TCOLMIN.md)          | 通过取行间最小值来归约每一列 |
| 2    | 19       | [TCOLPROD](../../header/tileblock/TCOLPROD.md)         | 通过跨行乘积来归约每一列 |
| 2    | 20       | [TCOLEXPAND](../../header/tileblock/TCOLEXPAND.md)       | 将每个源列的第一个元素广播到目标列 |
| 2    | 21       | [TCOLEXPANDADD](../../header/tileblock/TCOLEXPANDADD.md)    | 列广播加法：加上一个每列标量向量 |
| 2    | 22       | [TCOLEXPANDSUB](../../header/tileblock/TCOLEXPANDSUB.md)    | 列广播减法：从src0的每一列中减去一个每列标量向量src1 |
| 2    | 23       | [TCOLEXPANDMUL](../../header/tileblock/TCOLEXPANDMUL.md)    | 列广播乘法：将src0的每一列乘以一个每列标量向量src1 |
| 2    | 24       | [TCOLEXPANDDIV](../../header/tileblock/TCOLEXPANDDIV.md)    | 列广播除法：将src0的每一列除以一个每列标量向量src1 |
| 2    | 25       | [TCOLEXPANDMAX](../../header/tileblock/TCOLEXPANDMAX.md)    | 列广播最大值：与每列标量向量取最大值 |
| 2    | 26       | [TCOLEXPANDMIN](../../header/tileblock/TCOLEXPANDMIN.md)    | 列广播最小值：与每列标量向量取最小值 |
| 2    | 27       | [TCOLEXPANDEXPDIF](../../header/tileblock/TCOLEXPANDEXPDIF.md) | 列指数差运算：计算exp(src0 - src1)，其中src1为每列标量 |
| 2    | 28-31    | -                | 预留编码 |

### **复杂操作**

| Mode | Function | 操作             | 说明 |
|------|----------|------------------|------|
| 3    | 0-7      | -                | 预留编码 |
| 3    | 8        | [THISTOGRAM](../../header/templateblock/THISTOGRAM.md) | 累积直方图统计指令 |
| 3    | 9-29     | -                | 预留编码 |
| 3    | 30       | [ESAVE](../../header/templateblock/ESAVE.md)          | 异常保存块，用于保存发生异常的Tile块的块内状态 |
| 3    | 31       | [ERCOV](../../header/templateblock/ERCOV.md)          | 异常恢复块，用于恢复发生异常的Tile块的块内状态 |

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
