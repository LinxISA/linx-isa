# 0.41版本更新

更新日期：2024年9月29日

指令编码设计文档网页版路径请见[LinxISA Encoding-0.41](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:100519244765)

## 版本更新背景

灵犀指令集的下个重点目标是NPU和GPU的融合计算架构，其中最重要的指令扩展是SIMT执行模型。0.41版本就是用于描述基于块指令的SIMT执行模型的扩展实现。

不同于CPU中通过SIMD（单指令多数据）来处理矢量数据，GPU通常使用SIMT。SIMT的好处是无需开发者费力把数据凑成合适的矢量长度，并且SIMT允许每个线程有不同的分支。纯粹使用SIMD不能并行的执行有条件跳转的函数，因为条件跳转会根据输入数据不同在不同的线程中有不同表现，这个只有利用SIMT才能做到。

在LinxISA框架下，我们需要通过一套指令集融合NPU和GPU架构，做到新同构的要求。因此，我们在现有的框架下引入一种并行的块引擎，该引擎可同时处理N个块体相同的块指令，以达到对简单循环高效并行执行的效果。这种块引擎我们称为SIMT块指令。

SIMT块执行模型示意图如下：

![simt](../figs/isa/version/simt.png)

## 版本更新总体说明

1. 新增SIMT块指令定义
    - 增加SIMT块内微指令，统一采用**64bit长度编码**
    - SIMT块内定义**CSTK和PredM寄存器**。
    - SIMT块内定义了**4组相对索引寄存器**，分别命名为T,U,M,N，且每组包含8个寄存器。
2. 增加BTEXT指令，用于分离块中指示块头至块体的偏移距离
3. 标量块内新增loop.get和loop.set指令
4. 系统寄存器中增加只读寄存器LaneNum，用于存储SIMT块引擎并行lane的数量
5. 修改立即数偏移类的load/store指令的汇编语法。
6. 引入**浮点块**指令及**块内微指令**定义

## 变更详细介绍

### SIMT块指令定义

与传统标量块一样，SIMT块指令也通过BSTART指令作为块的起始指令，并且块头中增加必要的块描述指令补充执行控制信息。

1. **BSTART.SIMT**

指令编码：

![simt.bstart](../figs/isa/version/bstart.simt.png)

其中:

- 块类型BlockType编码为4b0011表示SIMT块，且**跳转类型固定为Fall**（编码为3b001）。
- 当前版本SIMT块定义为**分离块**，DCP位置为1。

2. **增加块体指针BTEXT指令**

为了扩展编码空间，SIMT块体内使用的都是64bit宽度的微指令。如果将这些64bit指令放在一体块内与32或16bit指令进行混编，硬件实现复杂度较高，实现周期比较长。
因此本版本将SIMT块定义为分离块，其块头中需要增加用于指示块体位置的BText指令。该指令用于编码SIMT块指令的块头至块体的偏移距离。

指令编码如下：

![btext-0.41](../figs/isa/version/btext-0.41.png)

3. **SIMT块架构状态**

- **全局状态**
    * R0-R23 ：SIMT块与传统标量块指令使用同一套第一层架构寄存器R0-R23。
- **系统状态**
    * **LaneNum** ：SIMT块在第一层架构引入了一个只读系统寄存器LaneNum，用于存储当前硬件支持的并行Lane的个数。 |
    * **LB0,LB1,LB2** ：SIMT块使用LB0,LB1,LB2 3个系统寄存器，用作并行迭代上限。 |
    * LC0,LC1,LC2 ：SIMT块使用LC0,LC1,LC2 3个系统寄存器，用作并行迭代次数控制。 |
- **块内状态**
    * **PredM** ：SIMT块内增加Predicate Mask掩码寄存器，用于控制SIMT块引擎中每个lane是否有效 |
    * **CSTK** ：Control Stack寄存器，用于SIMT块内出现分支时存储PC和掩码  |
    * **4组相对索引寄存器**：TR1至TR8，UR1至UR8，MR1至MR8，NR1至NR8。该类**寄存器宽度不固定**，可以是8, 16, 32或64位，具体由指令表达的寄存器宽度决定。

注意：本版本中对LB和LC类系统寄存器的SSRID有所调整。

4. **SIMT块内微指令**

一方面，由于SIMT块内引入了更多的私有寄存器，使得32bit空间下，不能通过5bit编码下所有可选寄存器；另一方面，SIMT块内微指令需要表明源和目的寄存器的宽度信息，并且指令操作数的类型有所扩展。这些原因导致SIMT块内一条指令无法使用32bit进行编码。

因此当前版本中，**SIMT块内微指令统一使用64bit编码长度**。这种64bit长指令定义为“一条32bit标准指令的低位拼接一条用于扩展的32bit指令LIEXT”，其中32bit标准指令可以是公共编码空间的指令，也可以是SIMT块内私有微指令。

Liext（全称Long Instruction Extend）指令用作与后面的基础指令进行拼接，组成一条64bit长指令。该指令的不同域段作为基础指令的对应域的扩展位。

指令编码如下：

![liext-0.41](../figs/isa/version/liext-0.41.png)

其中：

- **dest-ext**：该字段用作指令的目的寄存器域RegDst的扩展位。
- **func-ext**：该字段用作指令编码中func域的扩展位。
- **Src0-ext**：该字段用作指令第一个源寄存器域的扩展。
- **Src1-ext**：该字段用作指令第二个源寄存器域的扩展。
- **Src2-ext**：该字段用作指令第三个源寄存器域的扩展。

- **浮点多元运算类指令**

| 指令 | 汇编语法 | 指令定义 |
|------|-----------|---------|
| FADD | fadd SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 浮点加 |
| FSUB | fsub SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 浮点减 |
| FMUL | fmul SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 浮点乘 |
| FDIV | fdiv SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 浮点除 |
| FMADD | fmadd SrcL.{T}, SrcR.{T}, SrcA.{T}, ->{t,u,m,n}.{w} | 浮点乘加 |
| FMSUB | fmsub SrcL.{T}, SrcR.{T}, SrcA.{T}, ->{t,u,m,n}.{w} | 浮点乘减 |
| FNMADD | fnmadd SrcL.{T}, SrcR.{T}, SrcA.{T}, ->{t,u,m,n}.{w} | 浮点乘加，取负 |
| FNMSUB | fnmsub SrcL.{T}, SrcR.{T}, SrcA.{T}, ->{t,u,m,n}.{w} | 浮点乘减，取负 |

- **浮点一元运算类指令**

| 指令 | 汇编语法 | 指令定义 |
|------|-----------|---------|
| FABS | fabs SrcL.{T}, ->{t,u,m,n}.{w} | 绝对值 |
| FSQRT | fsqrt SrcL.{T}, ->{t,u,m,n}.{w} | 平方根 |
| FEXP | fexp SrcL.{T}, ->{t,u,m,n}.{w} | 以e为底的指数值 |
| FLOG | flog SrcL.{T}, ->{t,u,m,n}.{w} | 以2为底的对数值 |
| FSIN | fsin SrcL.{T}, ->{t,u,m,n}.{w} | 正弦值 |
| FCOS | fcos SrcL.{T}, ->{t,u,m,n}.{w} | 余弦值 |
| FRECIP | frecip SrcL.{T}, ->{t,u,m,n}.{w} | 求倒数 |

- **浮点类型判断指令**

| 指令 | 汇编语法 | 指令定义  |
|------|-----------|---------|
| FCLASS | fclass SrcL.{T}, ->{t,u,m,n}.{w} | 浮点类型判断  |

- **浮点比较指令**

| 指令 | 汇编语法 | 指令定义 |
|------|-----------|---------|
| FEQ | feq.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 相等比较（静默比较） |
| FNE | fne.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 不等比较（静默比较） |
| FLT | flt.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 小于比较（静默比较） |
| FGE | fge.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 大于等于比较（静默比较） |
| FEQS | feqs.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 相等比较（发信比较） |
| FNES | fnes.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 不等比较（发信比较） |
| FLTS | flts.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 小于比较（发信比较） |
| FGES | fges.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 大于等于比较（发信比较） |

- **浮点条件跳转指令**

| 指令 | 汇编语法 | 指令定义 |
|------|-----------|---------|
| B.FEQ | b.feq.srcT SrcL.{T}, SrcR.{T}, label | 相等跳转，否则顺序执行 |
| B.FNE | b.fne.srcT SrcL.{T}, SrcR.{T}, label | 不等跳转，否则顺序执行 |
| B.FLT | b.flt.srcT SrcL.{T}, SrcR.{T}, label | 小于则跳转，否则顺序执行  |
| B.FGE | b.fge.srcT SrcL.{T}, SrcR.{T}, label | 大于等于则跳转，否则顺序执行 |

- **数据类型转换指令**

数据类型转换指令用于支持浮点型数据格式之间以及浮点型向整型数据格式的转换操作。指令定义如下表：

| 指令 | 汇编语法 | 说明 |
|------|-----------|---------|
| FCVT  | fcvt  SrcL.{srcT}, ->{t,u,m,n}.{w}.{dstT} | 浮点型数据之间的格式转换 |
| FCVTI | fcvti SrcL.{srcT}, ->{t,u,m,n}.{w}.{dstT} | 浮点型向整型格式转换 |
| ICVT  | icvt  SrcL.{srcT}, ->{t,u,m,n}.{w}.{dstT} | 整型数据之间的格式转换 |
| ICVTF | icvtf SrcL.{srcT}, ->{t,u,m,n}.{w}.{dstT} | 整型向浮点型格式转换 |

- **最大最小值指令**

| 指令 | 汇编语法 | 指令定义 |
|------|-----------|---------|
| MAX  | max SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | 有符号整数最大值 |
| MAXU | maxu SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | 无符号整数最大值 |
| FMAX | fmax SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | 浮点数最大值 |
| MIN  | min SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | 有符号整数最小值 |
| MINU | minu SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | 无符号整数最小值 |
| FMIN | fmin SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | 浮点数最小值 |

- **标量运算指令**

| 指令 | 汇编语法 | 指令定义 |
|------|-----------|---------|
| DIV  | div  SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | 整数有符号除法 |
| DIVU | divu SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | 整数无符号除法 |
| REM  | rem  SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | 整数有符号求余 |
| REMU | remu SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | 整数无符号求余 |

- **条件选择指令**

| 指令 | 汇编语法 | 指令定义
|------|-----------|---------|
| CSEL | CSEL SrcP.{T}, SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | 条件选择指令 |

- **比特位运算指令**

| 指令 | 汇编语法 | 指令定义 |
|------|-----------|---------|
| REV16 | rev16 SrcL.{T}, ->{t,u,m,n}.{w} | 每16bit内大小端转换 |
| REV32 | rev32 SrcL.{T}, ->{t,u,m,n}.{w} | 每32bit内大小端转换 |
| REV64 | rev64 SrcL.{T}, ->{t,u,m,n}.{w} | 64bit内大小端转换 |
| CTZ | ctz SrcL.{T}, ->{t,u,m,n}.{w} | 有效位从低到高，计数第一个1之前0的位数 |
| CLZ | clz SrcL.{T}, ->{t,u,m,n}.{w} | 有效位从高到低，计数第一个1之前0的位数 |

- **内存申请和释放指令**

| 指令 | 汇编语法 | 指令定义 |
|------|-----------|---------|
| ALLOC | alloc size, ->{t,u,m,n}.{W} | 申请分配指定大小的内存空间 |
| FREE | free SrcL.d, size | 释放源寄存器中地址所在内存空间 |

- **Reduce指令**

Reduce指令用于将硬件的所有Lane中的处理结果进行汇总，并输出到全局寄存器Rd中。

| 指令 | 汇编语法 | 指令定义 |
|------|-----------|---------|
| RDADDU | rdaddu SrcL_v.{T}, =>Rd | 对所有lane中SrcL_v的值执行无符号相加操作，结果写到全局寄存器Rd中 |
| RDADDS | rdadds SrcL_v.{T}, =>Rd | 对所有lane中SrcL_v的值执行有符号相加操作，结果写到全局寄存器Rd中 |
| RDAND  | rdand SrcL_v.{T}, =>Rd | 对所有lane中SrcL_v的值按位与，结果写到全局寄存器Rd中 |
| RDOR   | rdor SrcL_v.{T}, =>Rd | 对所有lane中SrcL_v的值进行按位或，结果写到全局寄存器Rd中 |
| RDXOR  | rdxor SrcL_v.{T}, =>Rd | 对所有lane中SrcL_v的值进行按位异或，结果写到全局寄存器Rd中 |
| RDFADD | rdfadd SrcL_v.{T}, =>Rd | 将所有lane中SrcL_v中的浮点数相加，结果写到全局寄存器Rd中 |

- **最大/小值比较指令**

| 指令 | 汇编语法 | 指令定义 |
|------|-----------|---------|
| RDMAXU | rdmaxu SrcL_v.{T}, =>Rd | **无符号**比较所有lane中SrcL.< T>的值，将最大值写到全局寄存器Rd中。 |
| RDMAXS | rdmaxs SrcL_v.{T}, =>Rd | **有符号**比较所有lane中SrcL.< T>的值，将最大值写到全局寄存器Rd中。 |
| RDMINU | rdminu SrcL_v.{T}, =>Rd | **无符号**比较所有lane中SrcL.< T>的值，将最小值写到全局寄存器Rd中。 |
| RDMINS | rdmins SrcL_v.{T}, =>Rd | **有符号**比较所有lane中SrcL.< T>的值，将最小值写到全局寄存器Rd中。 | 
| RDFMAX | Rdfmax SrcL_v.{T}, =>Rd | 比较所有lane中SrcL.< T>中的浮点数，将最大值写到全局寄存器Rd中。 |
| RDFMIN | Rdfmin SrcL_v.{T}, =>Rd | 比较所有lane中SrcL.< T>中的浮点数，将最小值写到全局寄存器Rd中。 |

- **PC.PUSH/POP指令**

pc.push和pc.pop指令用于SIMT块内不同lane中执行路径上出现岔路时，保存和恢复重汇聚点的PC和掩码。

| 指令 | 汇编语法 | 说明 |
|------|-----------|---------|
| PC.PUSH | pc.push label | 将指令PC加偏移量得到的地址和当前lane的掩码压到Control Stack寄存器中。 |
| PC.POP | pc.pop | 将PC和掩码从Control Stack寄存器中 Pop出来并跳转到对应的地址以及设置掩码寄存器。 |

- **QPUSH/QPOP指令**

| 指令 | 汇编语法 | 说明 |
|------|-----------|---------|
| QPUSH | qpush SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | 把SrcR中的数据push到SrcL指定的GQM队列中，写入成功输出0，否则输出1至目的寄存器。|
| QPOP  | qpop  SrcL.{T}, ->{t,u,m,n}.{w}  | 读出SrcL指定的GQM队列中特定宽度的数据，结果写到目的寄存器中。 |

除了SIMT私有指令外，SIMT块内会使用到部分公共编码空间的指令，且同样采用原32bit编码前拼接一条LIEXT指令的方式进行编码。当前版本SIMT块内使用的公共指令列表如下：

- **算术运算指令**

| 指令列表 |
|----------|
| ADD, SUB, AND, OR, XOR, SRL, SRA, SLL |
| ADDI, SUBI, ANDI, ORI, XORI, SRLI, SRAI, SLLI |

- **比较指令**

| 指令 |
|------|
| CMP.EQ, CMP.NE, CMP.AND, CMP.OR, CMP.LT, CMP.GE, CMP.LTU, CMP.GEU | 
| CMP.EQI, CMP.NEI, CMP.ANDI, CMP.ORI, CMP.LTI, CMP.GEI, CMP.LTUI, CMP.GEUI |

- **比特位操作指令**

| 指令 |
|------|
| BXS, BXU, BIC, BIS | 

- **乘法指令**

| 指令 |
|------|
| MUL, MULU, MADD |

- **块内跳转指令**

| 指令 |
|------|
| JR, J |
| B.EQ, B.NE, B.LT, B.GE, B.LTU, B.GEU |

- **系统寄存器访问指令**

| 指令 |
|------|
| SSRGET, SSRSET |

- **内存加载load指令**

| 指令 |
|------|
| LB, LH, LW, LD,LBU,LHU, LWU, LBI, LHI, LWI, LDI |
| LBUI, LHUI, LWUI, LHI.U, LWI.U, LDI.U, LHUI.U, LWUI.U |

- **内存写Store指令**

| 指令 |
|------|
| SB, SH, SW, SD, SH.U, SW.U, SD.U |
| SBI, SHI, SWI, SDI, SHI.U, SWI.U, SDI.U |

- **长立即数和PC相对寻址指令**

| 指令 |
|------|
| ADDTPC, LUI |

## 增加微指令

本版本中，在基础指令集中增加如下的微指令用于设置循环寄存器。

| 指令 | 汇编语法 | 说明 |
|------|-----------|------|
| LOOP.GET | loop.get LoopReg, ->{t,u,m,n}.{w} | 读取循环寄存器值至块内私有寄存器 |
| LOOP.SET | loop.set SrcL, uimm, => LoopReg | 将寄存器SrcL加立即数uimm的结果设置到循环寄存器中 |

![loopgetset-0.41](../figs/isa/version/loopgetset-0.41.png)

## load/store指令修改

为了区分load/store-imm指令立即数地址偏移scaled和unscaled两种寻址方式，本版本对该类指令做出如下修改：

- 增加scaled和unscaled类的load/store指令汇编中立即数偏移的约束。
- 修改指令编码中立即数偏移的表达形式为：simm12或simm7。其中“simm”表示为有符号立即数偏移，后面的数字表示位数。

| load指令 | 汇编语法  | 备注 |
|------|-----------|----------|
| LBI | lbi [SrcL, simm], {->t, ->u, =>Rd} | simm是1的倍数，simm12编码为simm |
| LHI | lhi [SrcL, simm], {->t, ->u, =>Rd} | simm必须是2的倍数，simm12编码为simm/2 |
| LWI | lwi [SrcL, simm], {->t, ->u, =>Rd} | simm必须是4的倍数，simm12编码为simm/4 |
| LDI | ldi [SrcL, simm], {->t, ->u, =>Rd} | simm必须是8的倍数，simm12编码为simm/8 |
| LBUI | lbui [SrcL, simm], {->t, ->u, =>Rd} | simm是1的倍数，simm12编码为simm |
| LHUI | lhui [SrcL, simm], {->t, ->u, =>Rd} | simm必须是2的倍数，simm12编码为simm/2 |
| LWUI | lwui [SrcL, simm], {->t, ->u, =>Rd} | simm必须是4的倍数，simm12编码为simm/4 |
| LHI.U | lhi.u [SrcL, simm], {->t, ->u, =>Rd} | simm是1的倍数，simm12编码为simm |
| LWI.U | lwi.u [SrcL, simm], {->t, ->u, =>Rd} | simm是1的倍数，simm12编码为simm |
| LDI.U | ldi.u [SrcL, simm], {->t, ->u, =>Rd} | simm是1的倍数，simm12编码为simm |
| LHUI.U | lhui.u [SrcL, simm], {->t, ->u, =>Rd} | simm是1的倍数，simm12编码为simm |
| LWUI.U | lwui.u [SrcL, simm], {->t, ->u, =>Rd} | simm是1的倍数，simm12编码为simm |

以上load指令的访存地址为：`address = SrcL + simm`。

指令编码如下：

![load-0.41](../figs/isa/version/load-0.41.png)

| store指令 | 汇编语法  | 备注 |
|------|-----------|----------|
| SBI  | sbi SrcL, [SrcR, simm] | simm是1的倍数，simm12编码为simm |
| SHI  | shi SrcL, [SrcR, simm] | simm必须是2的倍数，simm12编码为simm/2 |
| SWI  | swi SrcL, [SrcR, simm] | simm必须是4的倍数，simm12编码为simm/4 |
| SDI  | sdi SrcL, [SrcR, simm] | simm必须是8的倍数，simm12编码为simm/8 |
| SHI.U  | shi.u SrcL, [SrcR, simm] | simm是1的倍数，simm12编码为simm |
| SWI.U  | swi.u SrcL, [SrcR, simm] | simm是1的倍数，simm12编码为simm |
| SDI.U  | sdi.u SrcL, [SrcR, simm] | simm是1的倍数，simm12编码为simm |

指令编码如下：

![store-0.41](../figs/isa/version/store-0.41.png)

| store指令 | 汇编语法  | 备注 |
|------|-----------|----------|
| SBI.A  | sbi.a SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm是1的倍数，simm7编码为simm |
| SHI.A  | shi.a SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm必须是2的倍数，simm7编码为simm/2 |
| SWI.A  | swi.a SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm必须是4的倍数，simm7编码为simm/4 |
| SDI.A  | sdi.a SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm必须是8的倍数，simm7编码为simm/8 |
| SHI.UA  | shi.ua SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm是1的倍数，simm7编码为simm |
| SWI.UA  | swi.ua SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm是1的倍数，simm7编码为simm |
| SDI.UA  | sdi.ua SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm是1的倍数，simm7编码为simm |

指令编码如下：

![store1-0.41](../figs/isa/version/store1-0.41.png)

以上store指令的访存地址为：`address = Srcr + simm`。

## 引入浮点块及浮点指令

为了进一步优化程序代码量，减少Codesize的膨胀，本次版本合入浮点块的设计，并增加了相关的浮点指令。

浮点块特点如下：

- 浮点块的起始指令为BSTART，同样支持32位和压缩版本编码。
- 浮点块不支持分离块形态，在汇编中通过“.fp”标识。
- 浮点块内寄存器的定义与标量块相同：**4个T + 4个U 寄存器**。

BSTART.fp编码（32bit）

![fp-0.41](../figs/isa/version/fp-0.41.png)

C.BSTART.fp编码（16bit）

![c.fp-0.41](../figs/isa/version/c.fp-0.41.png)

浮点块指令集中定义了如下的指令。

- 除法求余指令
- 位操作指令
- 最大最小值指令
- 条件选择指令
- 浮点指令
- 数据类型转换指令

其中：

浮点指令支持4种浮点数据类型：8bit低精度浮点数，16bit半精度浮点数，32bit单精度浮点数和64bit双精度浮点数。

浮点指令汇编格式为(以fadd为例)：`fadd.{T} SrcL, SrcR, {->t, ->u, =>Rd}`

- **{T}**：代指浮点指令的操作数类型，编码于“SrcType”域，编码方式见下表：

![fadd-0.41](../figs/isa/version/fadd-0.41.png)

| SrcType | 汇编标识 | 解释 |
|------|-----------|----------|
| 00 | fd | 操作数为64bit双精度浮点型数据 |
| 01 | fs | 操作数为32bit单精度浮点型数据 |
| 10 | fh | 操作数为16bit半精度浮点型数据 |
| 11 | fb | 操作数为8bit低精度浮点型数据 |

数据格式转换指令cvt的汇编格式为：`cvt.srcT2dstT SrcL, {->t, ->u, =>Rd}`

- srcT表示输入的数据格式，编码于“SrcType”域。
- dstT表示转换后的数据格式，编码于“DstType”域。

指令编码如下：

![fpcvt-0.41](../figs/isa/version/fpcvt-0.41.png)
