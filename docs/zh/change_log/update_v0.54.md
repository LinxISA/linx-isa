# 0.54版本更新

更新日期：2025年10月24日

指令编码设计文档网页版路径请见[LinxISA Encoding-0.54](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:101014747097)

## 一、更新背景

本次0.54版本主要用于对现有Tile块的执行模型进行改进，更新现有指令的命名，在细节上增加特定的约束并解决部分场景下的问题。

1. 通过细化Tile块分类，加强块类型定义和约束
2. 通过增加spill到S-tile寄存器上，解决部分场景下向量寄存器个数不足的问题。
3. 通过增加块内私有寄存器的个数选项来降低块内私有寄存器的个数，解决部分场景下向量寄存器个数过多带来的资源浪费问题。
4. 通过增加双输出Tile寄存器的指令，满足高性能场景下融合Tileop对输入输出Tile数量的需求。
5. 通过增加空Tile寄存器定义实现，解决控制流密集场景下在不同分支Tile寄存器索引距离不同的问题。
6. 通过增强地址连续Load/Store的定义，简化硬件识别连续Load/Store的实现。
7. 新增降维模式的开关，软件选择是否通过降维模式对特定场景进行性能优化。
8. 通过调整向量指令的命名，便于软件或程序员对标矢量指令的区分。
9. 通过增加Load/Store Local或Global的标志，便于硬件提前识别内存或Tile寄存器的访问。
10. 通过增加v.psel指令，加强对无效Lane结果的可控性以及实现对单边分支数据合并操作的优化。
11. 通过增加指令约束，解决发现的边角场景下的问题。

## 二、更新内容概要

灵犀指令集 0.54 版本在设计上做出了以下调整：

| 分类| 更新事项| 说明 |
|-----|--------|---------|
| 1. Tile块设计变更 | 1.1 更新Tile块分类和定义 | 用于细化Tile块分类，加强块类型定义。 |
|                  | 1.2 新增块内私有寄存器个数的选项 | 降低部分场景下向量寄存器资源浪费问题。 |
|                  | 1.3 增加私有的Tile寄存器定义 | Tile块可申请一下私有的Tile Register，用于块内的寄存器spill。 |
|                  | 1.4 新增空Tile寄存器定义 | 用于编译器分配寄存器时对齐索引距离。 |
|                  | 1.5 新增Tile寄存器双输出定义（增加TO1）| 满足高性能场景下融合Tileop对输入输出Tile数量的需求。 |
|                  | 1.6 B.ATTR指令标志位调整并与B.ARG指令合并 | 合并同类型指令以精简编码使用空间。(注意：删除B.ARG指令) |
|                  | 1.7 新增降维（DR）模式 | 满足不同场景的使用需要。 |
| 2. 指令设计扩展   | 2.1 向量指令命名调整 | 用于区分向量操作和标量操作 |
|                  | 2.2 加强地址连续load/store 定义 | 约束连续load/store的基址和偏移寄存器一定是标量寄存器 |
|                  | 2.3 Load/Store Bridge指令增加地址连续标记 | 用于使用桥接访存指令的同时提供地址连续的标记 |
|                  | 2.4 Load/Store指令增加区分访问local/global的标识 | 硬件提前识别内存或Tile寄存器访问，无需等地址算出来再判断，从而提升性能。 |
|                  | 2.5 增加V.PSEL指令 | 用于对单边分支的场景下数据的合并优化。 |
|                  | 2.6 增加指令约束 | setret必须放在BSTART后面，保证硬件预测器的性能 |
| 3. 系统块定义     | 3.1 系统块指令只支持FALL类型 | 删除其他跳转方式对应的BSTART编码 |

## 三、更新详细说明

### 1. Tile块设计扩展

Tile块是一类能够访问Tile寄存器的块指令。这类块指令为实现大规模张量运算而引入的，并通过将大算子分解为Tile级别的运算，结合硬件向量化/硬化处理等执行能力，来提升矩阵运算或向量运算等密集型计算任务的性能。

**1.1 Tile块分类**

新版本中，根据能否访问内存、是否有块体和执行方式等维度将Tile块分为以下几种具体块类型，以便于对每种块类型提供的针对性的定义或者约束。

Tile块分类如下：

| 分类/维度 | 能否访问内存 | 是否有块体 | Group间是否并行（内部计算是否可并行） | 备注 |
|----------|------------|------------|-------------------------------------|---------|
| **访存并行块（MPAR）** | 能 | 是 | 是 | 对应以前版本MCALL，且Parallel模式 |
| **访存串行块（MSEQ）** | 能 | 是 | 否 | 对应以前版本MCALL，且Vector模式   |
| **向量并行块（VPAR）** | 否 | 是 | 是 | 对应以前版本VCALL，且Parallel模式 |
| **向量串行块（VSEQ）** | 否 | 是 | 否 | 对应以前版本VCALL，且Vector模式   |
| **数据搬运块（TMA）**  | 能 | 否 | 是 | 对应TLoad/TStore/TCopy           |
| **矩阵数据块（CUBE）** | 否 | 否 | 是 | 对应矩阵运算和ACCCVT等            |

不同类型的Tile块可以有不同的块参数指令，用于配置本块的执行参数，具体见下表：

| 块参数 | B.ATTR | B.DIM | B.IOT/B.IOTI | B.IOR | B.IOD | B.TEXT | B.HINT |
|-------|--------|-------|-----------------|------|-------|--------|---------|
| MPAR  | 支持 | 支持 | 支持 | 支持 | 支持 | 支持 | 不支持  |
| MSEQ  | 支持 | 支持 | 支持 | 支持 | 支持 | 支持 | 不支持  |
| VPAR  | 支持 | 支持 | 支持 | 支持 | 支持 | 支持 | 不支持  |
| VSEQ  | 支持 | 支持 | 支持 | 支持 | 支持 | 支持 | 不支持  |
| TMA   | 支持 | 支持 | 支持 | 支持 | 支持 | 不支持 | 不支持 |
| CUBE  | 支持 | 支持 | 支持 | 不支持 | 不支持 | 不支持 | 不支持 |

BSTART汇编格式：

```asm
BSTART.MPAR <VS8, VS16>
BSTART.MSEQ <VS8, VS16>
BSTART.VPAR <VS8, VS16>
BSTART.VSEQ  <VS8, VS16>
BSTART.TMA TileOp, DataType
BSTART.CUBE TileOP, DataType
```

编码上，Tile块的BlockType字段统一编码为”5b00011”，并通过不同类型的Tile块的BSTART编码如下：

![bstart.tile](../figs/isa/version/0.54/bstart.tile.png)

对于有块体的Tile块，同时提供16bit的BSTART版本

![c.bstart.tile](../figs/isa/version/0.54/c.bstart.tile.png)

**1.2 新增向量寄存器使用数量的选项**

当前版本有块体的Tile块（包括MPAR/MSEQ/VPAR/VSEQ）块内我们提供了4组向量寄存器（vt/vu/vm/vn），每组4个。这些向量寄存器会占用大量物理寄存器资源。并且部分场景下，Tile块只会用到一至两组向量寄存器，从而造成寄存器资源阻塞，影响Tile块的执行效率。

因此，新版本我们给这4个Tile块提供了一个向量寄存器使用数量的选项。软件可以通过该选项指示本块使用的向量寄存器个数，便于硬件合理分配寄存器资源。

该信息表达在Tile块的BSTART指令上，汇编格式如下：
```asm
BSTART.MPAR <VS8, VS16>
BSTART.MSEQ <VS8, VS16>
BSTART.VPAR <VS8, VS16>
BSTART.VSEQ <VS8, VS16>
BSTART.MPAR <VS8, VS16>
BSTART.MSEQ <VS8, VS16>
BSTART.VPAR <VS8, VS16>
BSTART.VSEQ <VS8, VS16>
```

其中，“VS”等参数用于表达块内使用的向量寄存器数量（VS为Vector Size的简写）。

编码方式：

![c.bstart.tile](../figs/isa/version/0.54/bstart.tile1.png)

该参数编码在BSTART指令的Mode字段，编码方式如下：

| Mode编码 | 含义 | 说明 |
|----------|-------|------|
| 0 | **VS8** | 块内需要使用 2组向量寄存器，每组4个（共8个） |
| 1 | **VS16** | 块内需要使用4组向量寄存器，每组4个（共16个） |
| 2 | VS32(当前版本不支持) | 块内需要使用4组向量寄存器，每组8个（共32个） |
| 3 | VS64(当前版本不支持) | 块内需要使用4组向量寄存器，每组16个（共64个） |

注意事项：

- 软件申请的向量寄存器数量必须大于等于实际使用数量，否则硬件报非法参数异常。
- 16bit版本的C.BSTART.MPAR等没有Mode字段，默认使用全量的向量寄存器。

**1.3 增加私有的Tile寄存器**

由于向量并行块和向量串行块的内部不允许直接访问内存空间，没有线程栈的概念。因此也就无法实现函数调用、寄存器spill等依赖栈空间的功能，严重限制了块指令的计算能力和易用性。针对这一问题，我们提出如下的设计扩展：

**1.3.1 增加S寄存器**

在第一层架构中增加1类Tile Register，命名为S（全称为：Stack Tile Register）。该寄存器专门用作Tile块指令函数调用参数保存或者寄存器spill的栈空间。

**1.3.2 S寄存器使用方法**

- 与其他类型的Tile寄存器一样，Tile块指令通过B.IOT/B.IOTI指令来申请使用S寄存器。
- 不同的是，S寄存器是申请它的块指令私有的。S寄存器只对本块可见，块内可以对其读写。并且该寄存器随着块指令的提交而释放。
- B.IOT指令上申请的是一个Group内使用的栈空间大小，S寄存器总空间大小需要硬件计算。
- 注意：S寄存器Group容量乘以Group的个数得到的S寄存器的总空间大小，并且**该空间大小不能超过512KB**。

示例：
```asm
BSTART.VPAR <Row:64, Col:64, FP16>, T#1, U#1, ->T<16KB>, S<8KB>
// 展开形式
BSTART.VPAR FP16
B.DIM zero, 64, ->Row
B.DIM zero, 64, ->Col
B.IOTI T#1, U#1, group=0, ->S<8KB>    # 每个group申请的空间8KB
B.IOTI           group=1, ->T<16KB>
BSTART.VPAR <Row:64, Col:64, FP16>, T#1, U#1, ->T<16KB>, S<8KB>
// 展开形式
BSTART.VPAR FP16
B.DIM zero, 64, ->Row
B.DIM zero, 64, ->Col
B.IOTI T#1, U#1, group=0, ->S<8KB>    # 每个group申请的空间8KB
B.IOTI           group=1, ->T<16KB>
```

**1.3.3 形参寄存器**

块内增加一个Tile类型的形参寄存器TS，该寄存器映射到块头申请的S寄存器上。TS指向当前group内对应的栈空间。

寄存器spill示例：
```
// Spill
l.sd vt#1.ud, [TS, lc0<<3]
// Reload
l.ld [TS, LC0<<3], ->vt.d
// Spill
l.sd vt#1.ud, [TS, lc0<<3]
// Reload
l.ld [TS, LC0<<3], ->vt.d
```
注意事项：如果块内读取的是未初始化的TS，将返回随机值。

**1.4 新增空Tile寄存器定义**

Tile块指令允许输出到空Tile寄存器，用于编译器分配寄存器时对齐索引距离。

**1.4.1 场景示例**

在相对索引寄存器设计下，一个变量的生命周期跨控制流之后，由于不同控制流路径对该变量寄存器所属hand的写入次数可能不同，导致控制流汇合点使用该变量时可能存在多种索引距离。
```
if.entry:
     BSTART.VPAR  -> T<1KB>
     BSTART.COND  if.then, if.end
if.then:
     BSTART.MPAR  -> T<2KB>
     BSTART.MPAR  -> T<2KB>
     BSTART DIRECT  if.end 
if.end:
     TSTORE T#?, [a0]          # 将VCALL结果写回内存，此处存在2种索引距离
if.entry:
     BSTART.VPAR  -> T<1KB>
     BSTART.COND  if.then, if.end
if.then:
     BSTART.MPAR  -> T<2KB>
     BSTART.MPAR  -> T<2KB>
     BSTART DIRECT  if.end 
if.end:
     TSTORE T#?, [a0]          # 将VCALL结果写回内存，此处存在2种索引距离
```

为了解决上述问题，需要在if.entry代码段中额外插入一些输出至空Tile的指令来调整索引距离，使得if.end处2种索引距离相等。
```asm
if.entry:
     BSTART.VPAR -> T<1KB>
     BSTART.VPAR -> T<zero>    # 输出至空Tile寄存器  
     BSTART.VPAR -> T<zero>    # 输出至空Tile寄存器  
     BSTART.COND  if.then, if.end
if.then:
     BSTART.MPAR -> T<2KB>
     BSTART.MPAR -> T<2KB>
     BSTART DIRECT  if.end 
if.end:
     TSTORE T#3, [a0]
if.entry:
     BSTART.VPAR -> T<1KB>
     BSTART.VPAR -> T<zero>    # 输出至空Tile寄存器  
     BSTART.VPAR -> T<zero>    # 输出至空Tile寄存器  
     BSTART.COND  if.then, if.end
if.then:
     BSTART.MPAR -> T<2KB>
     BSTART.MPAR -> T<2KB>
     BSTART DIRECT  if.end 
if.end:
     TSTORE T#3, [a0]
```

**1.4.2 空Tile寄存器分配方法**

Tile块指令如果需要申请一个用于占位的空Tile寄存器，则必须通过B.IOT指令指示输出的Tile寄存器空间为0即可。空间为0的信息通过zero寄存器表达。

示例：
```asm
BSTART.VPAR ->T<zero>
BSTART.VPAR ->T<zero>
```
该指令展开为以下指令编码：
```asm
BSTART.VPAR VCALL
B.IOT group=0, ->T<zero>  # 通过zero寄存器表达申请空Tile reg
BSTART.VPAR VCALL
B.IOT group=0, ->T<zero>  # 通过zero寄存器表达申请空Tile reg
```

编码方式：RegSrc字段编码为zero寄存器。

![biot](../figs/isa/version/0.54/biot.png)

**1.5 B.ATTR与B.ARG指令合并**

为了精简指令编码，新版本中对B.ATTR指令修改如下：

- 删除hyper标记位，当前版本只有Tile块中支持块内跳转，并且不需要再指定hyper属性。
- 删除relay标记位，默认所有块指令都不relay。
- 删除scall标记位，与TRAP含义相同。
- TRAP标记位编码位置调整。
- 合入B.ARG指令的参数。
- 增加DR标志位（降维模式，详细介绍见1.7小节）

B.ARG指令的相关参数合入到B.ATTR后，删除B.ARG指令。

汇编格式：
```asm
B.ATTR {trap, atomic, <aq, rl, aqrl>, far, Layout.{canon, normal}, SrcType, PadValue, DR}
B.ATTR {trap, atomic, <aq, rl, aqrl>, far, Layout.{canon, normal}, SrcType, PadValue, DR}
```

编码格式

![battr](../figs/isa/version/0.54/battr.png)

其中，新增的降维模式标志位DR的编码方式为：

| DR | 含义 |
|----|-------|
| 0 | 多维模式 |
| 1 | 降维模式 |

**1.6 新增降维（DR）模式**

新版本中，我们提供了Tile块指令的三层循环的展开的两种方式。

- 降维模式（Dimension Reduction）：块体的三层迭代全部铺平展开，每64（对应当前设计下一个Group的laneNum）次迭代分配到一个Group内执行，直到迭代结束。
- 多维模式（Multi Dimension）：以块体的最内层迭代次数为粒度分Group，两次最内层迭代之间不允许分配到同一个Group中。

块体的循环展开实现为：
```asm
parallel_for（lc2 = 0; lc2 < lb2; lc2++）
    parallel_for（lc1 = 0; lc1 < lb1; lc1++）
        parallel_for（lc0 = 0; lc0 < lb0; lc0++）
              kernel(lane_id);
         end for
    end for
end for
parallel_for（lc2 = 0; lc2 < lb2; lc2++）
    parallel_for（lc1 = 0; lc1 < lb1; lc1++）
        parallel_for（lc0 = 0; lc0 < lb0; lc0++）
              kernel(lane_id);
         end for
    end for
end for
```

降维模式的示意图如下：

假设最内层循环次数为32, 硬件会将两次内层循环迭代调度到同一个group内执行。

![reducedim](../figs/isa/version/0.54/reducedim.png)

多维模式的示意图如下：

场景1：最内层循环上限值（LB0）小于等于64。图示如下：

![multidim](../figs/isa/version/0.54/multidim.png)

场景2：最内层循环上限值（LB0）大于64。图示如下：

![multidim1](../figs/isa/version/0.54/multidim1.png)

多维模型下，必须保证：

- 一个Group内LC0的值必须是连续的；
- 一个Group内LC1的值必须保持不变；
- 一个Group内LC2的值必须保持不变；

该模型下，一个Tile块拆分出来的Group的数量计算公式为：
```asm
if (LB0 % 64 > 0) 
    innerNum = LB0 / 64 +1;
else
    innerNum = LB0 / 64;
GroupNumber = LB2 * LB1 * innerNum;
if (LB0 % 64 > 0) 
    innerNum = LB0 / 64 +1;
else
    innerNum = LB0 / 64;
GroupNumber = LB2 * LB1 * innerNum;
```
多维模式更适合于地址连续load/store的使用场景，保证在一个Group内lc0是连续递增的。

### 2.指令设计扩展

**2.1 向量指令汇编重命名**

新版本中，为了便于区分标量和向量操作，Tile块内的向量指令命名统一修改为使用“V.”作为前缀，标量指令仍使用“L.”作为前缀。

指令列表列表如下：

| 原命名 | 向量指令命名 | 备注 | 原命名 | 向量指令命名 | 备注 |
|--------|------------|------|--------|-------------|---------|
| L.ADD,L.SUB,L.AND,L.OR,L.XOR<br>L.SRL,L.SRA,L.SLL<br>L.ADDI,L.SUBI,L.ANDI,L.ORI<br>L.XORI,L.SRLI,L.SRAI,L.SLLI | V.ADD,V.SUB,V.AND,V.OR<br>V.XOR,V.SRL,V.SRA,V.SLL<br>V.ADDI,V.SUBI,V.ANDI,V.ORI,<br>V.XORI,V.SRLI,V.SRAI,V.SLLI | 向量: vt/vu/vm/vn<br>标量: t/u, p | L.LW.ADD,L.LW.AND,L.LW.OR<br>L.LW.XOR,L.LW.MAX,L.LW.MIN<br>L.LD.ADD,L.LD.AND,L.LD.OR<br>L.LD.XOR,L.LD.MAX,L.LD.MIN | V.LW.ADD,V.LW.AND,V.LW.OR<br>V.LW.XOR,V.LW.MAX,V.LW.MIN<br>V.LD.ADD,V.LD.AND,V.LD.OR<br>V.LD.XOR,V.LD.MAX,V.LD.MIN | 向量: vt/vu/vm/vn<br>标量: t/u, p |
| L.CMP.EQ,L.CMP.NE,L.CMP.AND<br>L.CMP.ORL.CMP.LT,L.CMP.GE<br>L.CMP.LTU,L.CMP.GEU,L.CMP.EQI<br>L.CMP.NEI,L.CMP.ANDI,L.CMP.ORI<br>L.CMP.LTI,L.CMP.GEI,L.CMP.LTUI<br>L.CMP.GEUI | V.CMP.EQ,V.CMP.NE,V.CMP.AND<br>V.CMP.ORV.CMP.LT,V.CMP.GE<br>V.CMP.LTU,V.CMP.GEU,V.CMP.EQI<br>V.CMP.NEI,V.CMP.ANDI,V.CMP.ORI<br>V.CMP.LTI,V.CMP.GEI,V.CMP.LTUI<br>V.CMP.GEUI | 向量: vt/vu/vm/vn,p<br>标量: t/u<br>输出P时为向量 | L.SW.ADD,L.SW.AND,L.SW.OR<br>L.SW.XOR,L.SW.MAX,L.SW.MIN<br>L.SD.ADD,L.SD.AND,L.SD.OR<br>L.SD.XOR,L.SD.MAX,L.SD.MIN | V.SW.ADD,V.SW.AND,V.SW.OR<br>V.SW.XOR,V.SW.MAXV.SW.MIN<br>V.SD.ADD,V.SD.AND,V.SD.OR<br>V.SD.XOR,V.SD.MAX,V.SD.MIN | 任意输入为向量寄存器即为向量 |
| L.MUL, L.MADD, L.DIV, L.REM | V.MUL, V.MADD, V.DIV, V.REM | 向量: vt/vu/vm/vn<br>标量: t/u, p | L.FADD,L.FSUB,L.FMUL,L.FDIV<br>L.FMADD,L.FMSUB,L.FNMADD<br>L.FNMSUB | V.FADD,V.FSUB,V.FMUL,V.FDIV<br>V.FMADD,V.FMSUB,V.FNMADD<br>V.FNMSUB | 向量: vt/vu/vm/vn<br>标量: t/u, p |
| L.BXS,L.BXU,L.BIC,L.BIS,L.CTZ,L.CLS<br>L.BCNT,L.REV | V.BXS,V.BXU,V.BIC,V.BIS,V.CTZ,V.CLS<br>V.BCNT,V.REV | 向量: vt/vu/vm/vn<br>标量: t/u, p | L.FEQ,L.FNE,L.FLT,L.FGE,L.FEQU<br>L.FNEUL.FLTU,L.FGEU<br>L.MAX,L.MIN,L.FMAX,L.FMIN | V.FEQ,V.FNE,V.FLT,V.FGE,V.FEQU<br>V.FNEUV.FLTU,V.FGEU<br>V.MAX,V.MIN,V.FMAX,V.FMIN | 向量: vt/vu/vm/vn<br>标量: t/u, p |
| L.CSEL | V.CSEL | 向量: vt/vu/vm/vn<br>标量: t/u, p | L.FCVT,L.FCVTI,L.ICVT,L.ICVTF | V.FCVT,V.FCVTI,V.ICVT,V.ICVTF | 向量: vt/vu/vm/vn<br>标量: t/u, p |
| L.LB,L.LH,L.LW,L.LD,L.LBU,L.LHU<br>L.LWU,L.LBI,L.LHI,L.LWI,L.LDI,L.LBUI<br>L.LHUI,L.LWUIL.LHI.U,L.LWI.U,L.LDI.U<br>L.LHUI.U,L.LWUI.U | V.LB,V.LH,V.LW,V.LD,V.LBU,V.LHU<br>V.LWU,V.LBI,V.LHI,V.LWI,V.LDI,V.LBUI<br>V.LHUI,V.LWUIV.LHI.U,V.LWI.U,V.LDI.U<br>V.LHUI.U,V.LWUI.U | 向量: vt/vu/vm/vn<br>标量: t/u, p | L.FABS,L.FSQRT,L.FRECIP,L.FEXP<br>L.FLN,L.FCLASS | V.FABS,V.FSQRT,V.FRECIP,V.FEXP<br>V.FLN,V.FCLASS | 向量: vt/vu/vm/vn<br>标量: t/u, p |
| L.SB,L.SH,L.SW,L.SD,L.SH.U,L.SW.U<br>L.SD.U,L.SBI,L.SHI,L.SWI,L.SDI,L.SHI.U<br>L.SWI.U,L.SDI.U | V.SB,V.SH,V.SW,V.SD,V.SH.U,V.SW.U<br>V.SD.U,V.SBI,V.SHI,V.SWI,V.SDI,V.SHI.U<br>V.SWI.U,V.SDI.U | 任意输入为向量寄存器即为向量 | L.RDADD,L.RDAND,L.RDOR<br>L.RDXOR,L.RDFADD,L.RDMAX<br>L.RDMIN,L.RDFMAX,L.RDFMIN | V.RDADD,V.RDAND,V.RDOR<br>V.RDXOR,V.RDFADD,V.RDMAX<br>V.RDMIN,V.RDFMAX,V.RDFMIN | 只有向量版本 |
| L.LB.BRG,L.LH.BRG,L.LW.BRG,L.LD.BRG,<br>L.LBU.BRG,L.LHU.BRG,L.LWU.BRG<br>L.LBI.BRG,L.LHI.BRG,L.LWI.BRG<br>L.LDI.BRG,L.LBUI.BRG,L.LHUI.BRG<br>L.LWUI.BRG,L.LHI.U.BRG,L.LWI.U.BRG<br>L.LDI.U.BRG,L.LHUI.U.BRG,L.LWUI.U.BRG | V.LB.BRG,V.LH.BRG,V.LW.BRG,V.LD.BRG,<br>V.LBU.BRG,V.LHU.BRG,V.LWU.BRG<br>V.LBI.BRG,V.LHI.BRG,V.LWI.BRG<br>V.LDI.BRG,V.LBUI.BRG,V.LHUI.BRG<br>V.LWUI.BRG,V.LHI.U.BRG,V.LWI.U.BRG<br>V.LDI.U.BRG,V.LHUI.U.BRG,V.LWUI.U.BRG | 只有向量版本 | L.SHFL.UP,L.SHFL.DOWN<br>L.SHFL.BFLY,L.SHFL.IDX<br>L.SHFLI.UP,L.SHFLI.DOWN<br>L.SHFLI.BFLY,L.SHFLI.IDX | V.SHFL.UP,V.SHFL.DOWN<br>V.SHFL.BFLY,V.SHFL.IDX<br>V.SHFLI.UP,V.SHFLI.DOWN<br>V.SHFLI.BFLY,V.SHFLI.IDX | 只有向量版本 |
| L.SB.BRG,L.SH.BRG,L.SW.BRG,L.SD.BRG<br>L.SH.U.BRG,L.SW.U.BRG,L.SD.U,L.SBI.BRG<br>L.SHI.BRG,L.SWI.BRG,L.SDI.BRG<br>L.SHI.U.BRG,L.SWI.U,L.SDI.U.BRG | V.SB.BRG,V.SH.BRG,V.SW.BRG,V.SD.BRG<br>V.SH.U.BRG,V.SW.U.BRG,V.SD.U,V.SBI.BRG<br>V.SHI.BRG,V.SWI.BRG,V.SDI.BRG<br>V.SHI.U.BRG,V.SWI.U,V.SDI.U.BRG | 只有向量版本 | L.QPUSH,L.QPOP | V.QPUSH,V.QPOP | 向量: vt/vu/vm/vn<br>标量: t/u, p |

示例：
```asm
# 标量指令
l.add t#1, u#1, ->t
l.add t#1, p, ->p
l.ld [TS, offset], ->u
l.ld [TS, offset], ->p
l.sd t#1, [TO, offset]
l.sd p#1, [TO, offset]
# 向量指令：
v.add vt#1.uh, vu#1.uh, ->vt.h
v.add t#1, vu#1.uh, ->vt.h
v.sw vt#1.uw, [TO, lc0<<2]
v.ld [TA, lc0<<3], ->vt.d
```

**2.2 加强连续Load/Store 定义**

0.52.1版本中，为了简化硬件地址计算过程，高效地进行地址访问。指令集提供了一种地址连续的Load/Store指令，这类指令的地址由“基址寄存器”,“LC0寄存器偏移”和“偏移寄存器或立即数偏移” 三部分计算得到。

我们期望“基址寄存器”和“偏移寄存器或立即数偏移”是不变量，而LC0是一个跟随lane展开依次递增的变量，通过这样的方式达到group内访存地址的连续性。

其中部分指令汇编格式：
```asm
v.lw  [srcL.<T>, lc0<<2, srcR.<T>], ->dst.w
v.lwi [srcL.<T>, lc0<<2, imm], ->dst.w
v.sw  srcD.uw, [srcL.<T>, lc0<<2, srcR.<T>]
v.swi srcD.uw, [srcL.<T>, lc0<<2, imm]
v.lw  [srcL.<T>, lc0<<2, srcR.<T>], ->dst.w
v.lwi [srcL.<T>, lc0<<2, imm], ->dst.w
v.sw  srcD.uw, [srcL.<T>, lc0<<2, srcR.<T>]
v.swi srcD.uw, [srcL.<T>, lc0<<2, imm]
```

**2.2.1 指令约束**

为了保证一个group内访存地址的连续性，一方面要求架构设计上按照上述1.3节的定义分Group，另一方面还需要对这类访存指令的“基址寄存器SrcL”和“偏移寄存器SrcR”的使用增加约束：

- 地址连续的访存指令的 基址寄存器必须是标量寄存器或Tile寄存器，否则报非法指令异常。
- 地址连续的访存指令的 偏移寄存器必须是标量寄存器，否则报非法指令异常。
- 如果偏移寄存器的值由LC1/LC2计算得到，那么应保证该类指令在多维模式下使用，以确保一个Group内LC1和LC2不变。

示例：
```asm
v.lw  [ri0, lc0<<2, t#1], ->vt.w
v.lwi [TA, lc0<<2, 8],    ->vu.w
v.sw vt#1.uw, [TO, lc0<<2, ri1]
v.swi vu#1.uw, [ri2, lc0<<2, 8]
v.lw  [ri0, lc0<<2, t#1], ->vt.w
v.lwi [TA, lc0<<2, 8],    ->vu.w
v.sw vt#1.uw, [TO, lc0<<2, ri1]
v.swi vu#1.uw, [ri2, lc0<<2, 8]
```

图示如下：

![](../figs/isa/version/0.54/continuels.png)

**2.2.2 指令编码**

本版本对地址连续的Load/Store指令编码并无修改。其中访存指令的第12bit为地址连续的标志位，编码为1时软件应保证每个group内地址一定是连续的，否则允许地址不连续。

![](../figs/isa/version/0.54/vload.png)

**2.3 Load/Store bridge指令增加地址连续的标记**

为了满足软件同时使用Load/Store bridge操作以及提供地址连续Load/Store的需求，新版本中在Load/Store bridge指令上增加地址连续的标记。通过此标记降低硬件地址计算的开销。

**2.3.1 汇编格式**

与普通Load/Store指令相同，地址连续的Load/Store bridge指令在汇编中通过一个固定的LC0输入，来作为寻址偏移的一部分。

|指令 | 汇编格式 |
|------|--------|
| V.LB.BRG | `v.lb.brg<.local> [SrcL<.ud>, <lc0>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LH.BRG | `v.lh.brg<.local> [SrcL<.ud>, <lc0<<1>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LW.BRG | `v.lw.brg<.local> [SrcL<.ud>, <lc0<<2>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LD.BRG | `v.ld.brg<.local> [SrcL<.ud>, <lc0<<3>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LBU.BRG | `v.lbu.brg<.local> [SrcL<.ud>, <lc0>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LHU.BRG | `v.lhu.brg<.local> [SrcL<.ud>, <lc0<<1>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LWU.BRG | `v.lwu.brg<.local> [SrcL<.ud>, <lc0<<2>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LBI.BRG | `v.lbi.brg<.local> [SrcL<.ud>, <lc0>, simm], ->Dst.<W>` |
| V.LHI.BRG | `v.lhi.brg<.local> [SrcL<.ud>, <lc0<<1>, simm], ->Dst.<W>` |
| V.LWI.BRG | `v.lwi.brg<.local> [SrcL<.ud>, <lc0<<2>, simm], ->Dst.<W>` |
| V.LDI.BRG | `v.ldi.brg<.local> [SrcL<.ud>, <lc0<<3>, simm], ->Dst.<W>` |
| V.LBUI.BRG | `v.lbui.brg<.local> [SrcL<.ud>, <lc0>, simm], ->Dst.<W>` |
| V.LHUI.BRG | `v.lhui.brg<.local> [SrcL<.ud>, <lc0<<1>, simm], ->Dst.<W>` |
| V.LWUI.BRG | `v.lwui.brg<.local> [SrcL<.ud>, <lc0<<2>, simm], ->Dst.<W>` |
| V.LHI.UBRG | `v.lhi.ubrg<.local> [SrcL<.ud>, <lc0<<1>, simm], ->Dst.<W>` |
| V.LWI.UBRG | `v.lwi.ubrg<.local> [SrcL<.ud>, <lc0<<2>, simm], ->Dst.<W>` |
| V.LDI.UBRG | `v.ldi.ubrg<.local> [SrcL<.ud>, <lc0<<3>, simm], ->Dst.<W>` |
| V.LHUI.UBRG | `v.lhui.ubrg<.local> [SrcL<.ud>, <lc0<<1>, simm], ->Dst.<W>` |
| V.LWUI.UBRG | `v.lwui.ubrg<.local> [SrcL<.ud>, <lc0<<2>, simm], ->Dst.<W>` |
| V.SB.BRG | `v.sb.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0>, SrcR.<T>]`  |
| V.SH.BRG | `v.sh.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<1>, SrcR.<T><<1]` |
| V.SW.BRG | `v.sw.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<2>, SrcR.<T><<2]` |
| V.SD.BRG | `v.sd.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<3>, SrcR.<T><<3]` |
| V.SH.UBRG | `v.sh.ubrg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<1>, SrcR.<T>]` |
| V.SW.UBRG | `v.sw.ubrg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<2>, SrcR.<T>]` |
| V.SD.UBRG | `v.sd.ubrg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<3>, SrcR.<T>]` |
| V.SBI.BRG | `v.sbi.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0>, simm]` |
| V.SHI.BRG | `v.shi.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<1>, simm]` |
| V.SWI.BRG | `v.swi.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<2>, simm]` |
| V.SDI.BRG | `v.sdi.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<3>, simm]` |
| V.SHI.UBRG | `v.shi.ubrg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<1>, simm]` |
| V.SWI.UBRG | `v.swi.ubrg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<2>, simm]` |
| V.SDI.UBRG | `v.sdi.ubrg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<3>, simm]` |

使用地址连续的Load/Store bridge指令时，也必须保证满足2.2中对连续Load/Store指令的要求。

**2.3.2 指令编码**

同普通Load/Store指令， Load/Store bridge指令通过“C”标记位指示地址是否连续。

![vloadbrg](../figs/isa/version/0.54/vloadbrg.png)

全量指令编码请查看ISA Encoding Excel 文档。

**2.4 区分Local/Global访问**

为了硬件能够提前识别Tile Reg或者Global Memory访问，不需要等待地址计算出来再进行判断，从而达到提升性能的目的。0.54版本中，Load/Store指令增加显示表达访存Tile Reg的标识。

具体修改如下：

- 地址为Tile Register的Load/Store指令，汇编中增加”.local”后缀。
- 地址为Global Memory的Load/Store指令，汇编中不额外增加后缀。（默认访问共享内存）

汇编语法：
```asm
v.loadop<.local>  [baseReg, offset], ->dstReg
v.storeop<.local> dataReg, [baseReg, offset]
v.loadop<.local>  [baseReg, offset], ->dstReg
v.storeop<.local> dataReg, [baseReg, offset]
```
其中，“.local”是可选后缀，软件根据访存地址是否为Tile Register选择是否增加该后缀。

注意：软件/程序员应保证指令访问的地址分类无误。如果地址给错，硬件报异常。

指令编码上，增加1bit **L (local)** 标志位。访存Tile Register时编码为1，否则编码为0。编码如下：

![localload](../figs/isa/version/0.54/localload.png)

![localstore](../figs/isa/version/0.54/localstore.png)

此处仅粘贴部分load/store指令编码，全量内容请查看ISA Encoding Excel 文档。

**2.5 增加V.PSEL指令**

在向量计算中，某些通道（lane）可能因掩码控制、边界越界或分支屏蔽等原因被标记为无效。如何处理这些无效通道的输出值，对于控制数值正确性、存一致性以及后续计算行为具有重要意义。

为增强计算结果控制能力，Tile块指令中新增了 Predication Mode（pmode）定义，用于指定无效通道的计算结果如何处理。两种 pmode 模式定义：

- merging mode（合并模式）：无效通道的结果将保持为输入寄存器的原始值，适用于希望保留原数据、不产生突变的情形。
- zeroing mode（清零模式）：无效通道的结果强制写为 0，适用于需清除旧值或初始化输出的场景。

该机制使开发者可根据具体应用需求明确控制指令对无效通道的处理方式，避免依赖默认行为，提升了代码的可控性和可移植性。

当前定义下，Tile块的无效lane内的指令计算结果默认采用清零模式，即目的寄存器中填入0。因此新版本通过增加一条L.PSEL指令来实现合并模式。该指令定义如下：

**2.5.1 指令定义**

指令语义：根据寄存器SrcP内每一位掩码，选择左源寄存器或者右源寄存器的值写入目的寄存器中。掩码为1，选择左源寄存器SrcL；掩码为0，选择右源寄存器SrcR。

汇编语法：
```asm
v.psel SrcP, SrcL.<T>, SrcR.<T><.neg>, ->Dst.<W>
v.psel SrcP, SrcL.<T>, SrcR.<T><.neg>, ->Dst.<W>
```

- SrcP可以是P寄存器或者标量寄存器（标量寄存器内每一位读作一个lane的条件掩码）。
- SrcR支持可选的“.neg”参数，用于对SrcR操作数按位取反加一。

指令编码如下：

![psel](../figs/isa/version/0.54/psel.png)

**2.6 增加指令约束**

setret指令用于CALl块或ICALL块内记录返回地址至ra寄存器中。以前设计中，该指令可放在块体中的任何位置，并通过当前TPC加offset计算得到返回地址。

但在微架构实现过程中发现会存在如下问题：

- setret在IFU取到时触发将call_ret预测地址push进预测器。
- 若setret不是块内的第一条微指令，并且nuke_flush发生在setret指令之前，就会导致重复将call_ret预测地址push进预测器的行为，最终call_ret预测功能失效。

![setret](../figs/isa/version/0.54/setret.png)

因此新版本增加如下约束：**CALL或ICALL类型的块指令中，setret或 c.setret指令必须放在BSTART后面**。否则硬件触发非法指令异常。

**3. 系统块变更**

新版本中，系统块指令仅支持FALL顺延类型的块间跳转方式，因此删除其他跳转类型对应的编码。程序中条件跳转或者函数调用等可以通过整型标量块或者浮点标量块实现。

32bit编码：

![sysblock-32](../figs/isa/version/0.54/sysblock-32.png)

48t编码：

![sysblock-32](../figs/isa/version/0.54/sysblock-48.png)

64bit编码：

![sysblock-32](../figs/isa/version/0.54/sysblock-64.png)
