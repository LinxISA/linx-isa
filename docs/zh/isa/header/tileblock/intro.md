# 张量指令集

## **简介**

张量指令集是为并行计算和异构计算架构设计的一种指令集合，支持对形状可变的数据块（Tile）进行高效操作。数据块内具有特定的格式，能够处理大规模的并行计算任务，广泛应用于矩阵运算、深度学习、图像处理等领域。

---

## **TMA类指令**

TMA类指令主要用于内存操作，包括数据的加载、存储、复制、类型转换以及内存聚集和散布操作。关于这种块指令的详细介绍请见[访存数据块](../../blockIntro/tma_block/intro.md)。

| Mode | Function | 操作   | 说明 |
|------|----------|--------|------|
| 0    | 0        | [TLOAD](./TLOAD.md)      | 从内存ddr或remote向Tile寄存器拷贝 |
| 0    | 1        | [TSTORE](./TSTORE.md)    | 从Tile寄存器向内存ddr或remote拷贝 |
| 0    | 2        | [TMOV](./TMOV.md)        | Tile寄存器之间的数据移动/复制，支持存储布局的变换 |
| 0    | 3        | -                        | 保留 |
| 0    | 4        | [MGATHER](./MGATHER.md)  | 将离散的内存空间的数据聚集到Tile寄存器中 |
| 0    | 5        | [MSCATTER](./MSCATTER.md)| 将Tile寄存器中的数据存储到离散的内存空间 |
| 0    | 6-31     | -                        | 保留 |

---

## **CUBE类指令**

CUBE类指令主要用于矩阵和向量的乘法运算，包括基本矩阵乘法、带偏置的矩阵乘法、缩放矩阵乘法以及通用矩阵-向量乘法。关于这种块指令的详细介绍请见[矩阵数据块](../../blockIntro/cube_block/intro.md)。

### **矩阵乘法操作**

| Mode | Function | 操作             | 说明 |
|------|----------|------------------|------|
| 0    | 0        | [TMATMUL](./TMATMUL.md)               | 矩阵乘：A矩阵乘B矩阵，结果矩阵写到ACC寄存器 |
| 0    | 1        | [TMATMUL.BIAS](./TMATMUL.BIAS.md)     | 矩阵乘加：A矩阵乘B矩阵，加偏置矩阵，结果矩阵写到ACC寄存器 |
| 0    | 2        | [TMATMUL.ACC](./TMATMUL.ACC.md)       | 矩阵乘累加：A矩阵乘B矩阵，结果矩阵累加到ACC寄存器 |
| 0    | 3        | -              | 保留 |
| 0    | 4        | [TMATMULMX](./TMATMULMX.md)             | 缩放矩阵乘，结果写到ACC寄存器 |
| 0    | 5        | [TMATMULMX.BIAS](./TMATMULMX.BIAS.md)   | 缩放矩阵乘，加偏置矩阵，结果写到ACC寄存器 |
| 0    | 6        | [TMATMULMX.ACC](./TMATMULMX.ACC.md)     | 缩放矩阵乘，结果矩阵累加到ACC寄存器 |
| 0    | 7        | -              | 保留 |

### **固定管线操作**

| Mode | Function | 操作             | 说明 |
|------|----------|------------------|------|
| 0    | 8        | [ACCCVT](./ACCCVT.md)   | 将数据从ACC寄存器搬移到外部的T、U、M、N寄存器。在数据搬运期间支持转换操作 |
| 0    | 9-15     | -                | 保留 |

### **矩阵-向量乘法操作**

| Mode | Function | 操作             | 说明 |
|------|----------|------------------|------|
| 0    | 16       | [TGEMV](./TGEMV.md)                | 通用矩阵-向量乘法，结果写到ACC寄存器 |
| 0    | 17       | [TGEMV.BIAS](./TGEMV.BIAS.md)      | 通用矩阵-向量乘法，带偏置加法，结果写到ACC寄存器 |
| 0    | 18       | [TGEMV.ACC](./TGEMV.ACC.md)        | 通用矩阵-向量乘法，结果累加到ACC寄存器 |
| 0    | 19       | -              | 保留 |
| 0    | 20       | [TGEMVMX](./TGEMVMX.md)            | 通用缩放矩阵-向量乘法，结果写到ACC寄存器 |
| 0    | 21       | [TGEMVMX.BIAS](./TGEMVMX.BIAS.md)  | 通用缩放矩阵-向量乘法，带偏置加法，结果写到ACC寄存器 |
| 0    | 22       | [TGEMVMX.ACC](./TGEMVMX.ACC.md)    | 通用缩放矩阵-向量乘法，结果累加到ACC寄存器 |
| 0    | 23-31    | -              | 保留 |

---

## **TEPL类指令**

TEPL类指令主要用于对Tile数据块进行逐元素操作、标量操作以及按轴操作。关于这种块指令的详细介绍请见[模版数据块](../../blockIntro/tepl_block/intro.md)。

### **Tile-Tile逐元素操作**

| Mode | Function | 操作   | 说明 |
|------|----------|--------|------|
| 0    | 0        | [TADD](./TADD.md)   | 两个Tile的逐元素加法 |
| 0    | 1        | [TSUB](./TSUB.md)   | 两个Tile的逐元素减法 |
| 0    | 2        | [TMUL](./TMUL.md)   | 两个Tile的逐元素乘法 |
| 0    | 3        | [TDIV](./TDIV.md)   | 两个Tile的逐元素除法 |
| 0    | 4        | [TREM](./TREM.md)   | 两个Tile的逐元素余数，余数符号与除数相同 |
| 0    | 5        | [TFMOD](./TFMOD.md)  | 两个Tile的逐元素余数，余数符号与被除数相同 |
| 0    | 6        | [TAND](./TAND.md)   | 两个Tile的逐元素按位与 |
| 0    | 7        | [TOR](./TOR.md)     | 两个Tile的逐元素按位或 |
| 0    | 8        | [TXOR](./TXOR.md)   | 两个Tile的逐元素按位异或 |
| 0    | 9        | [TSHL](./TSHL.md)   | 两个Tile的逐元素左移 |
| 0    | 10       | [TSHR](./TSHR.md)   | 两个Tile的逐元素右移 |
| 0    | 11       | [TMAX](./TMAX.md)   | 两个Tile的逐元素最大值 |
| 0    | 12       | [TMIN](./TMIN.md)   | 两个Tile的逐元素最小值 |
| 0    | 13       | [TCMP](./TCMP.md)   | 比较两个Tile并写入一个打包的谓词掩码 |
| 0    | 14       | [TPRELU](./TPRELU.md) | 带逐元素斜率Tile的逐元素参数化ReLU |
| 0    | 15       | [TABS](./TABS.md)   | Tile的逐元素绝对值 |
| 0    | 16       | [TNOT](./TNOT.md)   | Tile的逐元素按位取反 |
| 0    | 17       | [TNEG](./TNEG.md)   | Tile的逐元素取负 |
| 0    | 18       | [TEXP](./TEXP.md)   | 逐元素指数运算 |
| 0    | 19       | [TLOG](./TLOG.md)   | Tile的逐元素自然对数 |
| 0    | 20       | [TRECIP](./TRECIP.md) | Tile的逐元素倒数 |
| 0    | 21       | [TSQRT](./TSQRT.md)  | 逐元素平方根 |
| 0    | 22       | [TRSQRT](./TRSQRT.md) | 逐元素倒数平方根 |
| 0    | 23       | [TRELU](./TRELU.md)  | Tile的逐元素ReLU |
| 0    | 24       | [TADDC](./TADDC.md)  | 三元逐元素加法：dst = src0 + src1 + src2 |
| 0    | 25       | [TSUBC](./TSUBC.md)  | 三元逐元素减法：dst = src0 - src1 + src2 |
| 0    | 26       | [TSEL](./TSEL.md)   | 使用掩码Tile在两个Tile之间进行选择（逐元素选择） |
| 0    | 27       | [TCVT](./TCVT.md)   | Tile的逐元素数据格式转换。 |
| 0    | 28-31    | -      | 保留 |

### **Tile逐元素和标量操作**

| Mode | Function | 操作   | 说明 |
|------|----------|--------|------|
| 1    | 0        | [TADDS](./TADDS.md)  | Tile与标量的逐元素加法 |
| 1    | 1        | [TSUBS](./TSUBS.md)  | 从Tile中逐元素减去一个标量 |
| 1    | 2        | [TMULS](./TMULS.md)  | Tile与标量的逐元素乘法 |
| 1    | 3        | [TDIVS](./TDIVS.md)  | 与标量的逐元素除法（Tile/标量或标量/Tile） |
| 1    | 4        | [TREMS](./TREMS.md)  | 与标量的逐元素余数：remainder(src, scalar) |
| 1    | 5        | [TFMODS](./TFMODS.md) | 与标量的逐元素余数：fmod(src, scalar) |
| 1    | 6        | [TANDS](./TANDS.md)  | Tile与标量的逐元素按位与 |
| 1    | 7        | [TORS](./TORS.md)    | Tile与标量的逐元素按位或 |
| 1    | 8        | [TXORS](./TXORS.md)  | Tile与标量的逐元素按位异或 |
| 1    | 9        | [TSHLS](./TSHLS.md)  | Tile按标量逐元素左移 |
| 1    | 10       | [TSHRS](./TSHRS.md)  | Tile按标量逐元素右移 |
| 1    | 11       | [TMAXS](./TMAXS.md)  | Tile与标量的逐元素最大值：max(src, scalar) |
| 1    | 12       | [TMINS](./TMINS.md)  | Tile与标量的逐元素最小值 |
| 1    | 13       | [TCMPS](./TCMPS.md)  | 将Tile与标量逐元素比较 |
| 1    | 14       | [TLRELU](./TLRELU.md) | 带标量斜率的LeakyReLU |
| 1    | 15-23    | -      | 预留编码 |
| 1    | 24       | [TADDSC](./TADDSC.md) | 带标量融合逐元素加法运算：dst = src0 + scalar + src1 |
| 1    | 25       | [TSUBSC](./TSUBSC.md) | 带标量融合逐元素减法运算：dst = src0 - scalar + src1 |
| 1    | 26       | [SELS](./TSELS.md)  | 使用掩码Tile在源Tile和标量之间进行选择（源Tile逐元素选择） |
| 1    | 27       | [TEXPANDS](./TEXPANDS.md) | 将标量广播到目标Tile中 |
| 1    | 28-31    | -      | 预留编码 |

### **按轴归约/广播操作**

| Mode | Function | 操作             | 说明 |
|------|----------|------------------|------|
| 2    | 0        | [TROWSUM](./TROWSUM.md)          | 通过对列求和来归约每一行 |
| 2    | 1        | [TROWMAX](./TROWMAX.md)          | 通过取列间最大值来归约每一行 |
| 2    | 2        | [TROWMIN](./TROWMIN.md)          | 通过取列间最小值来归约每一行 |
| 2    | 3        | [TROWPROD](./TROWPROD.md)         | 通过跨列乘积来归约每一行 |
| 2    | 4        | [TROWEXPAND](./TROWEXPAND.md)       | 将每个源行的第一个元素广播到目标行中 |
| 2    | 5        | [TROWEXPANDADD](./TROWEXPANDADD.md)    | 行广播加法：加上一个每行标量向量 |
| 2    | 6        | [TROWEXPANDSUB](./TROWEXPANDSUB.md)    | 行广播减法：从src0的每一行中减去一个每行标量向量src1 |
| 2    | 7        | [TROWEXPANDMUL](./TROWEXPANDMUL.md)    | 行广播乘法：将src0的每一行乘以一个每行标量向量src1 |
| 2    | 8        | [TROWEXPANDDIV](./TROWEXPANDDIV.md)    | 行广播除法：将src0的每一行除以一个每行标量向量src1 |
| 2    | 9        | [TROWEXPANDMAX](./TROWEXPANDMAX.md)    | 行广播最大值：与每行标量向量取最大值 |
| 2    | 10       | [TROWEXPANDMIN](./TROWEXPANDMIN.md)    | 行广播最小值：与每行标量向量取最小值 |
| 2    | 11       | [TROWEXPANDEXPDIF](./TROWEXPANDEXPDIF.md) | 行指数差运算：计算exp(src0 - src1)，其中src1为每行标量 |
| 2    | 12-15    | -                | 预留编码 |
| 2    | 16       | [TCOLSUM](./TCOLSUM.md)          | 通过对行求和来归约每一列 |
| 2    | 17       | [TCOLMAX](./TCOLMAX.md)          | 通过取行间最大值来归约每一列 |
| 2    | 18       | [TCOLMIN](./TCOLMIN.md)          | 通过取行间最小值来归约每一列 |
| 2    | 19       | [TCOLPROD](./TCOLPROD.md)         | 通过跨行乘积来归约每一列 |
| 2    | 20       | [TCOLEXPAND](./TCOLEXPAND.md)       | 将每个源列的第一个元素广播到目标列 |
| 2    | 21       | [TCOLEXPANDADD](./TCOLEXPANDADD.md)    | 列广播加法：加上一个每列标量向量 |
| 2    | 22       | [TCOLEXPANDSUB](./TCOLEXPANDSUB.md)    | 列广播减法：从src0的每一列中减去一个每列标量向量src1 |
| 2    | 23       | [TCOLEXPANDMUL](./TCOLEXPANDMUL.md)    | 列广播乘法：将src0的每一列乘以一个每列标量向量src1 |
| 2    | 24       | [TCOLEXPANDDIV](./TCOLEXPANDDIV.md)    | 列广播除法：将src0的每一列除以一个每列标量向量src1 |
| 2    | 25       | [TCOLEXPANDMAX](./TCOLEXPANDMAX.md)    | 列广播最大值：与每列标量向量取最大值 |
| 2    | 26       | [TCOLEXPANDMIN](./TCOLEXPANDMIN.md)    | 列广播最小值：与每列标量向量取最小值 |
| 2    | 27       | [TCOLEXPANDEXPDIF](./TCOLEXPANDEXPDIF.md) | 列指数差运算：计算exp(src0 - src1)，其中src1为每列标量 |
| 2    | 28-31    | -                | 预留编码 |

### **复杂操作**

| Mode | Function | 操作             | 说明 |
|------|----------|------------------|------|
| 3    | 0-7      | -                | 预留编码 |
| 3    | 8        | [THISTOGRAM](./THISTOGRAM.md) | 累积直方图统计指令 |
| 3    | 9-29     | -                | 预留编码 |
| 3    | 30       | [ESAVE](./ESAVE.md)          | 异常保存块，用于保存发生异常的Tile块的块内状态 |
| 3    | 31       | [ERCOV](./ERCOV.md)          | 异常恢复块，用于恢复发生异常的Tile块的块内状态 |
