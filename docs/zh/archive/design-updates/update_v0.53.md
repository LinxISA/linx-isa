# 0.53版本更新

更新日期：2025年8月4日

指令编码设计文档网页版路径请见[LinxISA Encoding-0.53.2](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:101071672597)

## 一、更新背景说明

随着人工智能特别是大模型推理场景的迅速发展，计算资源需求日益增长，AI芯片架构正面临算力密度、能效比和多样化精度支持等多重挑战。灵犀指令集作为面向AI芯片优化设计的块级指令集，需要在保持高效可编程性的同时，持续适配新兴计算需求。

本次 0.53 版本的更新背景主要包括以下三个方面：

1. **面向大模型推理的低精度计算支持需求增强**：当前主流大模型推理场景（如LLM、CV模型部署）广泛采用 INT4、FP4、FP6 等低比特精度数据格式，以显著压缩模型体积、降低存储带宽与功耗消耗。为了适配这一趋势，灵犀指令集需扩展对多种非标准低精度数据格式的表达和运算支持。
2. **块级执行模型对灵活性和效率的更高要求**：原有Tile块的指令模型在实际编译与执行中存在块结构限制刚性、ICache 压力大、指令复用难等问题，难以支持高密度并行指令融合和更复杂的数据流图调度。因此，需要对块执行语义与结构进行解耦，提升调度自由度和硬件执行效率。
3. **AI计算核心指令需求持续增加**：随着大模型推理中出现越来越多的 矩阵微核、多通道融合、混合精度乘加、非线性激活近似（如LUT）等操作，对 ISA 提出了更高的表达能力要求。指令集需要支持：
    - 可组合式矩阵运算流程（计算 + 量化 + 写出）
    - 灵活的预处理（如Merge、Saturate、Round）
    - 点积（dot）等结构性并行操作

## 二、更新内容概要

因此，灵犀指令集 0.53.0 在设计上做出了如下方向性调整：

- 引入新并行块执行模型（多块融合、形参支持）
- 扩展 FP4、INT4、FP6 数据格式及其矩阵运算、转换指令支持
- 精简不常用复杂函数类指令（如sin、cos、log），聚焦高频场景
- 优化寄存器释放信息的表达方式

| 分类 | 事项 | 说明 |
|------|-------|--------|
| **分离块执行模型变更** | 1. 块内索引全局寄存器从实参变为形参 | 降低vector PE的icache footprint压力，使能多个块的块体合并 |
| **并行块内微指令变更** | 1. 数据格式转换指令扩展 | 为了支持在更广泛的 AI 推理与边缘计算场景中的应用 |
|                       | 2. 并行块内指令精简 | 删除sin, cos, log等复杂操作 |
|                       | 3. 删除通用浮点计算指令的bf16和flb类型的操作数 | 特殊精度浮点数通过指定opcode表达 |
|                       | 4. 向量寄存器的kill信息改为reuse | 绝大多数场景下寄存器都被使用一次，因此改为reuse标记多次使用的寄存器 |
| **数据块指令修改**     | 1. Tile Register的kill信息改为reuse | 绝大多数场景下寄存器都被使用一次，因此改为reuse标记多次使用的寄存器 |
|                       | 2. 数据搬移指令增加相对索引的屏障 | 用于解决COPYIN和COPYOUT之间乱序执行无法表达数据依赖问题。 |
|                       | 3. 矩阵运算指令修订 | 只允许输出到ACC |
|                       | 4. 删除结果带转置类矩阵运算指令 | MAMULBT、MAMULBACT和MAMULB.ACCT。 |
|                       | 5. 新增ACCCVT指令 | 用于数据从ACC寄存器搬移到T/U/M/N寄存器过程中的FIXPIPE处理。 |
|                       | 6. 新增TCVT指令 | 用于对T/U/M/N寄存器内的数据的layout和元素类型做转换。 |
|                       | 7. B.ARG指令增加SrcType字段 | 适配TCVT的指令设计 |
|                       | 8. TCOPY指令简化实现 | 仅用于无数据格式转换场景下Tile 寄存器至Tile寄存器的拷贝 |
|                       | 9. TCOPYIN | 命名修改为TLOAD，并支持数据layout变换 |
|                       | 10. TCOPYOUT | 命名修改为TSTORE，并支持数据layout变换 |
|                       | 11. B.ARG指令增加PadValue字段 | 适配TLOAD的指令设计 |

## 三、更新详细介绍

### 1. 分离块块内修改为形参方式索引全局寄存器

对于块体执行逻辑一致，只是使用的全局寄存器不同的分离块。如果可以把块体内使用的全局寄存器做成一种形参，那么这个块体就可以被多个块指令复用，然后多个块指令的块头通过传递不同实参来调用。这种方式可以使能多个块的块体合并，有效降低PE的icache 取指压力。因此新版本，我们提出一种块内通过形参来索引全局寄存器的定义。

以前版本定义的分离块示例：
```asm
BSTART.PAR MCALL .L1_body <Row:64, Col:32> [a1, a2, s0], ->T<256B>
BSTART.PAR MCALL .L2_body <Row:32, Col:32> [a3, a4, a5], ->T<128B>
...
.L1_body:
    l.madd    lc0.uh, a1.uh, lc1.uh,   ->vu.w
    l.lw      [a2.sd, vu#1.sw<<2],     ->vt.w
    l.madd    lc1.uh, s0.uh, lc0.uh,   ->vu.w
    l.sw      vt#1.sw, [to.ud, vu#1.sw<<2]
    bstop
.L2_body:
    l.madd    lc0.uh, a3.uh, lc1.uh,   ->vu.w
    l.lw      [a4.sd, vu#1.sw<<2],     ->vt.w
    l.madd    lc1.uh, a5.uh, lc0.uh,   ->vu.w
    l.sw      vt#1.sw, [to.ud, vu#1.sw<<2]
bstop
```
以往版本中，即使两个块的块体执行逻辑相同，但是由于指令使用的全局寄存器不同，仍然需要定义两个块体，占用两份内存空间。

新版本的分离块示例：
```asm
BSTART.PAR MCALL .L1_body <Row:64, Col:32> [a1, a2, s0], ->T<256B>
BSTART.PAR MCALL .L1_body <Row:32, Col:32> [a3, a4, a5], ->T<128B>
...
.L1_body:
    l.madd    lc0.uh, ri0.uh, lc1.uh, ->vu.w      // ri0映射到块指令第1个输入GPR
    l.lw      [ri1.sd, vu#1.sw<<2],   ->vt.w      // ri1映射到块指令第2个输入GPR
    l.madd    lc1.uh, ri2.uh, lc0.uh, ->vu.w      // ri2映射到块指令第3个输入GPR
    l.sw      vt#1.sw, [to.ud, vu#1.sw<<2]
    bstop
```

新版本，我们要求分离块 块体内使用形参的方式索引全局寄存器，例如上面代码中的“ri0, ri1, ri2”。这样上面的两个MCALL块可以使用同一个块体，并且根据需要灵活的指定输入哪些GPR。

- 当第一个MCALL执行时，ri0映射到a1，ri1映射到a2，ri2映射到s0。
- 当第二个MCALL执行时，ri0映射到a3，ri1映射到a4，ri2映射到a5。

通过这种实现方式，可以将原来的两个块体合并为一个，减轻PE icache取指压力。

新版本，我们定义了16个形参寄存器，其中包括12个输入和4个输出：

- 12个输入寄存器分别命名为RI0-RI11。（RI – Register Input）
- 4个输出寄存器分别命名为RO0-RO3。（RO – Register Output）

示例：
```asm
  BSTART.PAR MCALL .L1_body <Row:64, Col:32> [a1, a2, a1], ->T<256B>                  ；允许输入GPR重复
  BSTART.PAR MCALL .L3_body <Row:64, Col:32> [a1, a2, a1], ->T<256B> [s0, s0, s1]    ；不允许输出GPR重复
```
寄存器索引编码修改如下：

![formal-reg](../figs/isa/version/0.53/formal-reg.png){ width="800" }

同时为了适配上述修改，并行块内指令对zero寄存器的索引编码也有所更新，编码修改如下：
 
![zero-reg](../figs/isa/version/0.53/zero.png){ width="800" }

### 2.数据格式转换指令修改

为了支持灵犀指令集在更广泛的 AI 推理与边缘计算场景中的应用，尤其是在资源受限环境中部署大模型的能力，0.53 版本在数据格式支持与转换指令方面进行了系统性增强及其特殊解码方式。

2.1 已支持格式

在前一版本中，灵犀指令集已支持如下主流数据格式：

| 格式名称 | 格式说明 |
|---------|-------------|
| FP64 | 64bit双精度浮点数（e11m52）|
| FP32 | 32bit单精度浮点数（e8m23） |
| FP16 | 16bit半精度浮点数（e5m10） |
| FP8  | 8bit 低精度浮点数（e4m3）  |
| BF16 | 16bit半精度浮点数（e8m7）  |
| FP8  | 8bit 低精度浮点数（e5m2）  |
| S64/32/16/8 | 64/32/16/8 bit 有符号整数 |
| U64/32/16/8 | 64/32/16/8bit 无符号整数  |

但随着推理模型日益庞大，进一步压缩模型存储、减小带宽压力的需求日益迫切。为此，新版本新增如下内容： 

| 格式名称 | 位宽 | 结构 | 说明 |
|---------|-------|-----|-----------|
| TF32 | 32b | e8m10 | 高速训练格式   |
| HF32 | 32b | e8m11 | 高动态范围格式   |
| HiF8 | 8b | 厂商自定义低精度数据格式 | 特定模型压缩优化 |
| SF8 | 8b | e8m0 | 动态范围编码、稀疏表示 |
| FP6 | 6b | e3m2 / e2m3 | 极限压缩浮点数 |
| FP4 | 4b | e2m1 / e1m2 | 超低精度浮点数 |
| HiF4 | 4b | 厂商自定义低精度数据格式 | 特定模型压缩优化 |
| S/U4 | 4b | 有符号/无符号整数 | 边缘推理常用 |

对于非标准的数据格式，不提供专门的计算类指令，可以通过转换指令（Convert）将非标准数据格式转换为标准格式再进行计算，然后转换回原格式。

2.3 数据格式转换指令类型

灵犀支持如下四类格式转换指令，全部支持低精度格式：

- FCVT：浮点转浮点 : `l.fcvt.{st2dt} SrcL.<T>, ->Dst.<W>`
- FCVTI：浮点转整型 ：`l.fcvti.{st2dt} SrcL.<T>, ->Dst.<W>`
- ICVTF：整型转浮点 : `l.icvtf.{st2dt} SrcL.<T>, ->Dst.<W>`
- ICVT：整型转整型 : `l.icvt.{st2dt} SrcL.<T>, ->Dst.<W>`

汇编示例：
```asm
    l.fcvt.f162f32 vt#1.fh, ->vt.w
    l.fcvti.f322s8 vt#2.fs, ->vt.b
    l.icvtf.s162f8 vu#3.sh, ->vt.b
    l.icvt.s322s4 vu#4.sw, ->vt.b
```

2.4 指令编码更新

- 指令编码中扩展了 SrcType 与 DstType 字段，支持所有新增格式。
- L.ICVT和L.ICVTF的function字段有更新。

指令编码如下：
 
![cvt](../figs/isa/version/0.53/cvt.png){ width="800" }

2.5 转换示例

| 操作目标 | 汇编示例 |
|----------|-------------|
| FP32 → FP8 | `l.fcvt.f322f8 vt#1.fs, ->vt.b`  |
| FP8 → S8   | `l.fcvti.f82s8 vt#2.fb, ->vt.b`  |
| S8 → FP16  | `l.icvtf.s82f16 vt#3.sb, ->vt.h` |
| S32 → S4   | `l.icvt.s322s4 vt#4.sw, ->vt.b`  |

### 3.移除变种浮点计算

当前版本删除变种浮点计算，其中包括BF16, FP8(E5M3)等格式。

![removebf16](../figs/isa/version/0.53/removebf16.png){ width="800" }

本版本不支持变种数据格式的浮点计算，但提供Convert指令。将变种数据格式转换为标准数据格式进行计算。

### 4.并行块内指令精简

升级到0.5版本后并行块内支持不同长度指令混编，地址计算以及系统寄存器访问操作可以使用32bit版本，因此移除64bit版本。另一方面，对于正弦余弦以及求对数等运算指令硬件实现困难较大，可以通过其他指令组合实现，因此删除。

删除指令列表如下：

| 分类 | 指令 |
|--------------------|-------------------|
| 长立即数加载/地址计算 | l.addtpc, l.lui |
| 系统寄存器访问        | l.ssrget, l.ssrset |
| 复杂计算类            | l.fsin, l.fcos, l.flogb |

删除指令编码如下：
 
![const](../figs/isa/version/0.53/const.png){ width="800" }

![ssrget](../figs/isa/version/0.53/ssrget.png){ width="800" }

![fsin](../figs/isa/version/0.53/fsin.png){ width="800" }

### 5. 向量寄存器的kill信息改成reuse信息

上个版本中，为了提升寄存器使用效率，软件可以对并行块内的向量寄存器主动增加“.kill”信息来指示该寄存器是最后一次使用，并且使用后可以释放掉。

新版本修改为通过增加“.reuse”信息来指定该寄存器仍然会被使用，暂时不允许释放。对于最后一次使用的寄存器则通过不增加“.reuse”的方式来指定该寄存器使用后可以释放掉。

例如：
```asm
    l.add vt#1.sw, vt#2.reuse.sw, ->vt.w     # 本指令提交后，不允许硬件释放掉vt#2寄存器。
    l.ldi [vu#4.ud, 8],           ->vt.d      # 本指令提交后，允许硬件释放掉vu#4寄存器。
```

注意事项:

- 所有支持读向量寄存器的指令都支持主动释放本指令读取的向量寄存器。
- 当不确定后序指令是否使用该寄存器时，需要增加reuse标记。
- 标量寄存器不需要标记reuse信息。
- 向量寄存器被释放后，如果存在后序指令读取该寄存器，硬件应产生异常。也就是只有最后一次使用（last use）的寄存器可以主动释放。

### 6.Tile Register的kill信息改为reuse信息

为了提升Tile Register的利用率，上个版本中为并行块指令提供了主动释放本块读取的Tile寄存器的定义，即不再被使用的寄存器增加kill信息。

本版本我们修改为使用“.reuse”信息来指定哪些寄存器仍然会被使用，不允许硬件释放。汇编格式如下：
```asm
分离块：TileOP body_label, <LB0:Arg0, LB1:Arg1, LB2:Arg2> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, [BGetList], ->DstTileType<TileSize>, [BSetList]
模版块：TileOP <Row:Arg0, Col:Arg1, Dep:Arg2, DataType> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, [BGetList], ->DstTileType<TileSize>, [BSetList]
```
示例：
```
  TADD     <Row: 64, Col: 64, FP16> T#7.reuse, T#2, ->T<32KB>     ; 本指令提交后T#2允许释放，T#7不允许。
  TCOPYOUT <Row: 64, Col: 64, FP32> U#4.reuse, [a0]                ; 本指令提交后，U#4不允许释放
```
Tile Register是否保留（reuse）的信息编码在B.IOT或B.IOTI指令上，这两条指令更新后的定义如下：

汇编格式：
```asm
  B.IOT  [SrcTile0<.reuse>, SrcTile1<.reuse>], group={0,1}, ->DstTile<RegSrc>    # 通过寄存器RegSrc设置输出Tile的大小
  B.IOTI [SrcTile0<.reuse>, SrcTile1<.reuse>], group={0,1}, ->DstTile<Size>      # 通过立即数Size设置输出Tile的大小
```

编码格式：

![biot](../figs/isa/version/0.53/biot.png){ width="800" }

指令编码方式修改如下：

- S0K标志位修改为S0R(Reuse Source0)：该标志位用于指示本指令提交后，SrcTile0是否保留。编码为1时表示保留，不允许释放；编码为0则允许释放。
- S1K标识为修改为S1R(Reuse Source1)：该标志位用于指示本指令提交后，SrcTile1是否保留。编码为1时表示保留，不允许释放；编码为0则允许释放。
- DT位与DstTile字段共同编码组成3bit输出寄存器字段。

| DT:DstTile | 编码 | 解释 |
|-------------|---------|----------|
| 3b000 | 输出至T寄存器队列 |
| 3b001 | 输出至U寄存器队列 |
| 3b010 | 输出至M寄存器队列 |
| 3b011 | 输出至N寄存器队列 |
| 3b100 | 输出至ACC寄存器队列 |
| 3b101 – 3b110 | 保留 |
| 3b111 | 无效输出 |

### 7. 块指令增加相对索引的屏障

在前面的设计中，TCOPYIN和TCOPYOUT等数据搬移类指令之间如果读写的是同一片内存空间，但是使用了不同的全局寄存器传递内存首地址时，硬件实现无法提前判断这两条指令之前的依赖关系。此时如果对它们做乱序执行就会导致执行出错。例如：

```asm
  TADD T#1, U#1, ->T<8KB>
  TCOPYOUT  T#1, [a2]             ;将tile寄存器内的数据搬移到a2指定的地址内存中
  TCOPYIN   [a1]，->T<4KB>        ;将a1指定的地址内存中的数据搬移到tile寄存器中
  ...
```

如果a2和a1中存储了相同的内存首地址，这时TCOPYIN应该等待TCOPYOUT执行完成之后再执行。

因此，新版本我们增加一种屏障（barrier）机制，指示数据搬移指令之间的依赖关系。具体而言就是在指令中增加D（dependency）信息。

```asm
  MCALL label, <LB0:Arg0, LB1:Arg1, LB2:Arg2> SrcTile0, SrcTile1, SrcTile2, [BGetList], DepSrc, ->DstTileType<TileSize>, [BSetList], DepDst
```

其中：

- DepSrc表达对前序指令的依赖，可以指定对前序D索引距离为1至8的指令的依赖。例如D#1表示必须等待前面最近一条写到D的指令提交后再执行。
- DepDst表达对后序指令的屏障，实际汇编中表达为D。

同时需要增加一条新指令B.IOD（Block Input and Output Dependency）用于编码依赖信息。

汇编格式：`B.IOD DepSrc, ->DepDst`

指令编码：

![biod](../figs/isa/version/0.53/biod.png){ width="800" }

DepSrc和DepDst字段编码方式如下依赖关系表所示：

| 输入输出编码 | DepSrc | DepDst  |
|-------------|---------|----------|
| 5'b00000 | 无依赖 | 无输出  |
| 5'b00001 | D#1 | D        |
| 5'b00010 | D#2 | reserve  |
| 5'b00011 | D#3 | reserve  |
| 5'b00100 | D#4 | reserve  |
| 5'b00101 | D#5 | reserve  |
| 5'b00110 | D#6 | reserve  |
| 5'b00111 | D#7 | reserve  |
| 5'b01000 | D#8 | reserve  |
| others   | reserve | reserve |

模版块TCOPYIN和TCOPYOUT可以表达为：

```asm
TCOPYIN  <Row:Arg0, Col:Arg1, Dep:Arg2, DataType>, [RegSrc],  DepSrc,          -> DstTileType<TileSize>, DepDst
TCOPYOUT <Row:Arg0, Col:Arg1, Dep:Arg2, DataType>, SrcTile, [RegSrc], DepSrc, -> DstDep
```

示例：
```asm
TCOPYOUT t#1, [a2], ->d            ; I0
TCOPYIN [a3]，d#1,  ->T            ; I1, 等待I0提交后执行
TCOPYOUT t#1, [a4], ->d            ; I2
TCOPYIN [a5]，d#2,  ->T            ; I3, 等待I0提交后执行
TCOPYIN [a1]，d#1,  ->T, d         ; I4, 等待I2提交后执行
TCOPYOUT t#1, [a0], d#1            ; I5, 等待I4提交后执行
```

- 提交表示Tcopyout将数据全部写到内存。
- TCopyout按照顺序写入内存，硬件内存模型保证TCopyout不会乱序执行。因此TCopyin D#1依赖于前序的Copyout代表着copyin前序所有的copyout都写入内存提交后（注：写入SCB）才开始执行。

### 8.矩阵运算指令补充定义

8.1 对已有矩阵运算指令的修订

- 为了简化硬件实现，新版本中，矩阵运算指令的结果**仅允许输出到ACC寄存器**，不支持直接写到T/U/M/N等Tile register。
- ACC中数据格式**固定为FP32或INT32**，存储分形格式为**大N小Z**，**小Z的大小是1024Byte**。
- 为了保证设计统一性，矩阵运算指令不再支持对结果矩阵进行存储转置。然后增加一条ACCCVT指令用于将数据从ACC寄存器导出至T/U/M/N等，同时支持FixPipe处理。

经过上述修改后，保留原有的MAMULB、MAMULBAC和MAMULB.ACC指令，并**删除MAMULBT、MAMULBACT和MAMULB.ACCT**这3条对结果矩阵进行转置的指令。

| Opcode | Function | TileOP | 说明 |
|---------|----------|-----------|----------|
| **2-CUBE** | 0 | MAMULB      | 矩阵乘：A矩阵 乘 B矩阵，结果矩阵写到ACC寄存器 |
|            | 1 | MAMULBAC    | 矩阵乘加：A矩阵 乘 B矩阵，加C矩阵，结果矩阵写到ACC寄存器 |
|            | 2 | MAMULB.ACC  | 矩阵乘累加：A矩阵 乘 B矩阵，加ACC矩阵，结果矩阵写到ACC寄存器 |

1）MAMULB

汇编格式：`MAMULB <M:Arg0, N:Arg1, K:Arg2, DataType> SrcTile0<.reuse>, SrcTile1<.reuse>, ->ACC<TileSize>`
本模版块拆分为以下指令进行编码：
```asm
    BSTART.PAR MAMULB, DataType
    B.DIM  reg, imm,   ->M
    B.DIM  reg, imm,   ->N
    B.DIM  reg, imm,   ->K
    B.IOT  [SrcTile0<.reuse>, SrcTile1<.reuse>], group=0, ->ACC<TileSize>
```

2）MAMULBAC

汇编格式：`MAMULBAC <M:Arg0, N:Arg1, K:Arg2, DataType> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, ->ACC<TileSize>`
本模版块拆分为以下指令进行编码：
```asm
    BSTART.PAR MAMULBAC, DataType
    B.DIM  reg, imm,   ->M
    B.DIM  reg, imm,   ->N
    B.DIM  reg, imm,   ->K
    B.IOT  [SrcTile0<.reuse>, SrcTile1<.reuse>], group=0, ->ACC<TileSize>
    B.IOT  [SrcTile2<.reuse>], group=1
```
3）MAMULB.ACC

汇编格式：`MAMULB.ACC <M:Arg0, N:Arg1, K:Arg2, DataType> SrcTile0<.reuse>, SrcTile1<.reuse>, ACC#1, ->ACC<TileSize>`
本模版块拆分为以下指令进行编码：
```asm
    BSTART.PAR MAMULB.ACC, DataType
    B.DIM  reg, imm,   ->M
    B.DIM  reg, imm,   ->N
    B.DIM  reg, imm,   ->K
    B.IOT  [SrcTile0<.reuse>, SrcTile1<.reuse>], group=0, ->ACC<TileSize>
```

8.2 矩阵运算支持低精度数据格式

本版本中，指令集中保留3条用于矩阵乘或乘累加的数据块指令（TileOp），并且支持了如下数据格式：

因此，新版本我们对矩阵运算指令增加更多低精度数据类型的数据支持，包括INT4和FP4等。

示例：`MAMULB <M:128, N:32, K:64, S4> T#1, U#1, ->ACC<64KB>`

这条矩阵乘指令拆分为以下指令进行编码：
```asm
    BSTART.PAR MAMULB, S4
    B.DIM  zero, 128,   ->M
    B.DIM  zero, 32,    ->N
    B.DIM  zero, 64,    ->K
    B.IOTI  [T#1, U#1], ->T<64KB>
```
其中元素数据类型通过BSTART.PAR指令的DataType字段进行编码，因此新版本对该字段编码方式有所调整，修改后定义如下：

![bstart.par](../figs/isa/version/0.53/bstart.par.png){ width="800" }

| 编码 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| DataType | FP64 | FP32 | TF32 | HF32 | FP16 | BF16 | HiF8 | e4m3 | e5m2 | e3m2 | e2m3 | e2m1 | e1m2 | e8m0 | HiF4 | reserve |
| 编码 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 |
| DataType | S64 | S32 | S16 | S8 | S4 | reserve | reserve | reserve | U64 | U32 | U16 | U8 | U4 | reserve | reserve | reserve |

8.3 CUBE输入的存储格式

基于灵犀指令集的硬件实现中，CUBE运算单元的输入支持如下的存储布局。软件在进行矩阵运算前，应保证输入必须按照如下布局进行排布，否则执行结果不可知。

- Matrix A：采用大N小z的存储布局。
- Matrix B：采用大Z小n的存储布局。
- Matrix C：采用大Z小z的存储布局。

输入示意图如下：

![layout](../figs/isa/version/0.53/layout.png){ width="900" }

其中，矩阵A和矩阵C都必须以**大N小z**的布局进行存储，矩阵B以**大Z小n**的布局进行存储。

假设S0和K0分别为K维度分形大小的字节数和元素个数。不同的硬件实现，S0的大小不同（S0默认使用32Byte，对应一个分形大小为512Byte）。那么：

- 矩阵A的分形矩阵大小是`16 x K0`的。
- 矩阵B的分形矩阵大小是`K0 x 16`的。
- 矩阵C的分形矩阵大小是`16 x 16`的。

K0可以通过以下公式计算得到： `K0 = S0 / sizeof(DataType)`;   # DataType表示元素数据类型

当输入按照是上述的存储布局排布的，那么默认输出格式是大N小z的。如果想要把结果矩阵的存储布局改为其他格式，用于后序指令运算，那么可以使用TCVT指令改存储布局，并且将数据写到T,U,M,N寄存器中。

### 9.ACCCVT 数据搬移与随路处理支持

为增强灵犀指令集对后处理路径中数据转换与激活/量化等操作的支持，0.53版本新增 ACCCVT 指令（AccTile Convert）。该指令用于将矩阵乘计算后的结果从 ACC 寄存器搬移至外部 Tile 寄存器（如 T/U/M/N），并在搬移过程中融合量化、激活、逐元素操作等随路处理能力。

9.1 硬件路径与执行机制

ACCCVT指令设计的初衷，是为了解决 “矩阵乘后结果在写入 Tile Register 前仍需执行一系列格式转换与处理” 的性能瓶颈问题。

在灵犀架构中，矩阵乘法单元 CUBE Core 的计算结果，首先被写入内部的累加寄存器 ACC。而 ACC 到 Tile Register 的搬运路径上，专门设置了一条可编程的固定功能处理流水线（FixPipe），即 随路处理路径。

FixPipe 是由多个紧耦合的硬件模块串接组成的微型流水线，支持以下随路计算能力：

* 激活函数单元（ReLU、ClipReLU）
* 量化模块（支持 INT4/INT8、定点 scale/zp）
* 元素级计算单元（Add、Mul 等）
* 稀疏数据过滤与压缩单元
* 输出位掩码控制单元

这些模块按需由 `ACCCVT` 指令通过 `B.ARG` 编码选择启用，在数据从 ACC 输出至 Tile 寄存器过程中，直接就完成了对应的格式/结构/精度转换，具备极高吞吐率。
 
9.2 ACCCVT 指令

指令格式：
```
ACCCVT.{Layout.{canon, normal}} <Row:Arg0, Col:Arg1, DstType> ACC, ->DstTileType<TileSize>
```

- Layout: 指示数据搬移过程中存储格式转换的操作，当前版本支持NORM, NZ2ND，NZ2DN等。
- DstType：表示格式转换后Tile内元素的数据类型。
- DstTileType：用于指示目的寄存器，可选T/U/M/N等。

该指令的操作码定义如下：

| Opcode | Function | TileOP | 说明 |
|--------|----------|---------|--------|
| 2-CUBE | 8 | ACCCVT | 将数据从ACC寄存器搬移到外部的T,U,M,N寄存器。在数据搬运期间支持转换操作。 |

ACCCVT指令只支持ACC输入，不支持T/U/M/N寄存器输入。

```asm
    BSTART.PAR ACCCVT, DstType    # 隐含包含ACC输入
    B.ARG  Layout.{canon, normal}
    B.DIM  reg, imm,   ->ROW
    B.DIM  reg, imm,   ->COL
    B.IOT  [], group=0, ->{T, U, M, N}<TileSize>
```

操作配置：通过 B.ARG 指令设置 ACCCVT 的功能模式，避免使用 SSR 寄存器配置，提升代码清晰度与指令集一致性。

汇编格式：`B.ARG Layout.{canon, normal}`

- canon(canonicalize): 将输入ACC中矩阵的分形转换成标准左矩阵格式（标准左矩阵的分形容量是512byte，为Z分形），基于不同的数据格式将ACC的原分形进行合并或者拆分。
- normal：不对输入ACC中矩阵的原分形做变换。

canon操作的示意图如下：

![fixpipe](../figs/isa/version/0.53/fixpipe.png){ width="700" }

示例：`矩阵Q x (矩阵K^T) x 矩阵V `
```asm
COPYIN [a0], ->T<4KB>                                    # 矩阵Q（row major）
COPYIN [a1], ->T<4KB>                                    # 矩阵K (column major)
COPYIN [a2], ->T<4KB>                                    # 矩阵V (row major)
MAMULB <M:32, N:32, K:32, FP32> T#3, T#2, ->ACC<4KB>
ACCCVT.NORM.canon <Row:32, Col:32, FP32> ACC, ->T<4KB>  # 将ACC矩阵标准化，并写入T寄存器。
MAMULB <M:32, N:32, K:32, FP32> T#1, T#2, ->ACC<4KB>
ACCCVT.NZ2ND.normal <Row:32, Col:32, FP32> ACC, ->T<4KB> # 将ACC矩阵转换为ND格式，并写入T寄存器。
COPYOUT T#1, [a4] 
```

### 10.TCVT转换操作

10.1 指令格式：
```
TCVT.{Layout}, SrcType, <Row:Arg0, Col:Arg1, DstType> SrcTile.<reuse>, ->DstTileType<TileSize>
```
- Layout: 指示数据搬移过程中存储格式转换的操作。
- SrcType：表示输入Tile内元素的数据类型。
- DstType：表示格式转换后输出Tile内元素的数据类型。
- SrcTile：输入Tile寄存器，不允许是ACC寄存器。
- DstTileType：输出Tile寄存器，不允许是ACC寄存器。

TCVT指令拆分为以下指令进行编码：
```asm
BSTART.PAR TCVT, DstType
B.ARG  Layout, SrcType
B.DIM  reg, imm,   ->ROW
B.DIM  reg, imm,   ->COL
B.IOT  [SrcTile.<reuse>], group=0, ->{T, U, M, N}<TileSize>
```

10.2 B.ARG修改

为了适配TCVT的指令功能，B.ARG指令增加SrcType字段（编码方式如下），用于指定输入Tile中元素的数据格式。

![barg](../figs/isa/version/0.53/barg.png){ width="700" }

SrcType字段编码方式如下：

| 编码 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|------|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SrcType | FP64 | FP32 | TF32 | HF32 | FP16 | BF16 | HiF8 | e4m3 | e5m2 | e3m2 | e2m3 | e2m1 | e1m2 | e8m0 | HiF4 | reserve |
| 编码 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 |
| SrcType | S64 | S32 | S16 | S8 | S4 | reserve | reserve | reserve | U64 | U32 | U16 | U8 | U4 | reserve | reserve | invalid |

### 11.TCOPY修改

更新后，TCOPY指令用于无格式转换场景下Tile 寄存器至Tile寄存器的数据拷贝。

11.1 汇编格式

```asm
TCOPY SrcTile.<reuse>, ->DstTileType<TileSize>
```

该模版块拆分为以下指令进行编码：
```asm
BSTART.PAR TCOPY
B.IOT [SrcTile.<reuse>], group=0, -> DstTileType<TileSize>  #如果通过立即数指定输出大小，需使用B.IOTI指令
```

### 12.TCOPYIN修改

为了对齐到PTO指令集的定义，0.53.2版本中将TCOPYIN指令命名修改为**TLOAD**。TLOAD指令用于将数据从内存拷贝到Tile寄存器中，拷贝过程中支持修改数据的存储布局（layout）。

当前版本，TLOAD指令仅支持对内存中一至两维数据的加载。

12.1 汇编格式

```asm
TLOAD.Layout <LB0:ColValid, LB1:RowValid, LB2:Col, DataType, PadValue>, [RegSrc0, RegSrc1], DepSrc, -> DstTileType<TileSize>, DepDst
```
该模版块拆分为以下指令进行编码：
```asm
BSTART.PAR TLOAD, DataType
B.ARG  Layout, PadValue
B.DIM  reg, imm, ->LB0      # ColValid
B.DIM  reg, imm, ->LB1      # RowValid
B.DIM  reg, imm, ->LB2      # Col
B.IOT  group=0, ->DstTileType<TileSize>  #如果通过立即数指定输出大小，需使用B.IOTI指令
B.IOR  RegSrc0, RegSrc1
B.IOD  DepSrc, ->DepDst
```

12.2 B.ARG指令修改

为了适配TLOAD的设计，新版本B.ARG指令增加PadValue参数。该参数编码方式如下：

| PadValue编码 | 说明 |
|-------------|-------|
| 0 | Zero |
| 1 | Max |
| 2 | Min |
| 3 | Null |
| others | 保留 |

修改后B.ARG指令编码如下：

![barg1](../figs/isa/version/0.53/barg1.png){ width="700" }

### 13.TCOPYOUT修改

为了对齐到PTO指令集的定义，0.53.2版本中将TCOPYOUT指令命名修改为**TSTORE**。

TSTORE指令用于将数据从Tile寄存器拷贝到内存中，拷贝过程中支持修改数据的存储布局（layout），以便灵活应用到不同场景中。

13.1汇编格式

```asm
TSTORE.Layout <LB0:ColValid, LB1:RowValid, LB2:Col, DataType>, SrcTile, [RegSrc0, RegSrc1], DepSrc, -> DepDst
```

该模版块拆分为以下指令进行编码：
```asm
BSTART.PAR TSTORE, DataType
B.ARG  Layout
B.DIM  reg, imm,   ->LB0    # ColValid
B.DIM  reg, imm,   ->LB1    # RowValid
B.DIM  reg, imm,   ->LB2    # Col
B.IOT  SrcTile, group=0
B.IOR RegSrc0, RegSrc1
B.IOD DepSrc, ->DepDst
```
