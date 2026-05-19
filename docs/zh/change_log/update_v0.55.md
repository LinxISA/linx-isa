# 0.55版本更新

更新日期：2025年11月17日

指令编码设计文档网页版路径请见[LinxISA Encoding-0.55](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:101082569709)

## 一、更新背景

- 异常处理与调试：完善了异常/中断处理流程，加强了调试功能支持。
- 指令集扩展：新增了V.MOV指令、缩放矩阵乘法指令（MAMULBMX系列）和DMA指令，优化了向量处理和矩阵运算能力。
- 寄存器调整：扩展了BARG寄存器的功能，并新增了EBPCN寄存器，提升了块指令的控制能力和异常处理能力。
- 架构支持：新增基于PTO指令集的模版块指令，为第一层架构状态的评估提供了支持。

## 二、更新概要

灵犀指令集0.55版本包括三个子版本（0.55.0、0.55.1、0.55.2），每个子版本针对不同的功能模块进行了优化和增强。以下是各子版本的主要更新内容：

### 0.55.0版本

| 分类 | 修改事项 | 说明 |
|------|---------|---------|
| 1. **异常处理相关** | 1.1 不同块类型的BSTATE定义 | 用于对当前版本的不同块类型进行精细化设计 |
|                    | 1.2 更新EBSTATE实现       | 适配部分Tile块无法访问内存的设计 |
|                    | 1.3 加强异常处理设计       | 加入Tile块的异常保存处理 |
|                    | 1.4 更新特权级切换设计     | 特权级切换的过程中增加针对Tile块的处理 |
|                    | 1.5 修改部分系统寄存器     | 适配当前版本块指令异常保存和恢复的设计 |
|                    | 1.6 修订acrc/acre指令定义 | acrc/acre提交后立即触发异常用于实现精准异常 |
| 2. **软件调试相关** | 2.2 EBREAK指令加强定义    | 增加立即数参数便于在GDB外支持kprobe/uprobe等其它调试能力，立即数含义由内核定义 |
|                    | 2.2 增加16bit版本C.EBREAK指令 | 16bit版本用于GDB调试时可以安全地替换任意地址处的指令而不破坏下一条指令 |

### 0.55.1版本

| 分类 | 修改事项 | 说明 |
|------|---------|---------|
| 1. **新增指令** | V.MOV指令 | 新增一条不受全局P-Mask控制的向量指令，用于在控制流分支中全拷贝寄存器内容。 |
|                | 缩放矩阵乘法指令 | 新增MAMULBMX、MAMULBMXAC和MAMULBMX.ACC指令，支持微缩放机制，提升矩阵乘法的数值动态范围和表达能力。 |
|                | DMA指令 | 新增MCOPY.D指令和dma指令，支持通过DMA进行内存数据搬运。 |
| 2. **指令修订** | FENCE指令 | 同步0.43-Beta版本的指令设计，将FENCE.D改名为DSB，FENCE.I改名为ISB，并增加DSB指令的标记位M。 |
|                | ESAVE和ERCOV指令 | 修订为多输入多输出指令，支持块内上下文的保存和恢复，并增加对块体起始TPC的保存和恢复。 |
| 3. **寄存器调整** | BARG寄存器 | 扩展BPC和BPCN字段为64位，增加BlockType、Type、Taken、AQ、RL等字段，提升块指令的控制能力和异常处理。 |
|                  | 新增EBPCN寄存器 | 用于保存块指令发生异常后的下一个块指令BPC，确保异常处理后程序能够正确恢复执行。 |

### 0.55.2版本

1. **新增模版块指令**：新增 70+ 条模版块指令旨在优化第一层架构的状态管理，提升指令集的灵活性和可扩展性。

---

## 三、详细说明

### **1.1 BSTATE加强定义**

灵犀指令集中，一个块执行单元的内部状态称为BSTATE。BSTATE是一组与块执行相关的寄存器组，不同块执行单元（块类型）可能使用不同格式的BSTATE。BSTATE又分为BARG、TPC与LPR三部分。其中BARG代表与指令调度和执行相关的控制和状态寄存器，TPC指向块内正在执行的块体指令的地址，LPR代表当前块的私有寄存器组。BSTATE的定义如下:

| 名称 | 描述 |
|------|-------|
| BARG（Block Arguments Register Group） | 用于记录块指令在一层架构的调度和执行信息以及块内部的状态信息。 |
| TPC (Temporal Program Counter) | 微指令指针寄存器，用于指示正在执行的块内微指令的地址。 |
| LPR（Local Purpose Register） | 块指令内部的通用寄存器。 |

**1.1.1 BARG的定义**

BARG是一个寄存器组，由以前版本的CARG演进而来。现在设计中，BARG中不仅包含块指令提交时的信息，还存储着块指令的调度信息和执行属性，因此改名为BARG更符合定义。
BARG寄存器包含一系列不同的字段，每个字段允许被对应的指令单独设置。并且每个字段允许在特定的块类型下是有效的，具体如下：

| 字段 | 位宽 | 描述 | 有效块类型 |
|------|------|------|----------|
| BPC | 64 | 当前块指令的BPC | 所有块类型 |
| BPCN | 64 | 执行逻辑中下个块指令的BPC相对本块BPC的偏移量。 | STD, FP |
| LRA | - | 分离块中本地返回地址相对于本块BPC的偏移量。（复用BPCN字段） | MPAR, MSEQ, VPAR, VSEQ |
| BlockType | 5 | 当前块的块类型 | 所有块类型 |
| Type | 2 | 跳转方式 | STD, FP |
| Taken | 1 | 跳转taken标记位  |  STD, FP |
| AQ,RL | 2 | 执行序属性 | STD, SYS, FP, VPAR, VSEQ |
| RegDst0 | 5 | 记录分离块第1个输出GGPR  | MPAR, MSEQ, VPAR, VSEQ |
| RegDst1 | 5 | 记录分离块第2个输出GGPR  | MPAR, MSEQ, VPAR, VSEQ |
| RegDst2 | 5 | 记录分离块第3个输出GGPR  | MPAR, MSEQ, VPAR, VSEQ |
| RegDst3 | 5 | 记录分离块第4个输出GGPR  | MPAR, MSEQ, VPAR, VSEQ |

说明：

- MPAR,MSEQ,VPAR,VARQ等定义为分离块结构，因此LRA字段有效。
- STD和FP块支持全量跳转方式，因此BPCN，TYPE，TAKEN字段有效。
- TMA和CUBE块是硬化实现的块指令，内部无法编程。因此只有BPC。
- MPAR,MSEQ块默认带有AQ,RL属性（详见内存模型MCALL模式）。
- RegDst0~RegDst3字段通过块头中的B.IOR指令初始化。如果该字段无效，编码为0。

BARG的域段定义如下图所示：

![barg](../figs/isa/version/0.55/barg.png)

其中，BPCN_OFFSET和LRA_OFFSET复用同一个字段，该字段存储内容由块类型决定。

**1.1.2 TPC定义**

TPC用于记录块内执行的微指令的地址。

- 对于整型标量块、系统块和标量浮点块，块内只有一个TPC。
- 对于访存并行块和向量并行块，每个并行Group内都有一个独立的TPC。
- 对于访存串行块和向量串行块，块内group间串行，因此只有一个TPC。
- 对于TMA和CUBE块，块内部不可编程，因此无TPC。

**1.1.3 LPR定义**

同样，LPR也包含了一系列寄存器，并且在不同的块类型中内容有所不同：

| 寄存器 | 寄存器位宽 | 描述 | 有效块类型 |
|-------|-----------|------|------------|
| **T/U**   | 64bit | 标量寄存器 | STD, SYS, FP, MPAR, MSEQ, VPAR, VSEQ  |
| **RI/RO** | 64bit | 形参寄存器 | MPAR, MSEQ, VPAR, VSEQ |
| **PRED(P)** | 64bit | 掩码寄存器 | MPAR, MSEQ, VPAR, VSEQ |
| **LB** | 16x4 bit | Lane总数器 | MPAR, MSEQ, VPAR, VSEQ |
| **LC** | 16x4 bit | Lane计数器 | MPAR, MSEQ, VPAR, VSEQ |
| **VT/VU/VM/VN** | 32bit x LaneNum | 向量寄存器 | MPAR, MSEQ, VPAR, VSEQ |
| **Output Tile** | 512Byte ~ 32KB | 输出Tile寄存器 | MPAR, MSEQ, VPAR, VSEQ, TMA, CUBE |

### **1.2 EBSTATE更新定义**

发生异常或者被中断的块指令的块内状态称为EBSTATE。以前版本中，EBSTATE保存在EBSTATEP指向的内存空间中。由于0.5版本引入了Tile块并且部分Tile块不允许访问内存，因此EBSTATE的存储方式进行如下调整。

**1.2.1 EBSTATE保存与恢复**

新版本中，不同块类型的EBSTATE的存储方式定义如下：

| 块类型 | 保存BSTATE至EBSTATE  | 从EBSTATE恢复 |
|--------|----------------------|----------------|
| STD, SYS, FP | 需要硬件保存：<br>将BPC保存至SSR:EBPC; <br>将BARG中其余信息保存至SSR:EBARG中; <br>将TPC保存至SSR:ETPC; <br>软件选择性保存：<br>将T/U等标量寄存器保存至Memory中。 | 需要硬件恢复：<br>从SSR:EBPC中恢复BPC； <br>从SSR:EBARG恢复跳转信息等至BARG；<br>从SSR:ETPC恢复TPC；<br>软件选择性恢复：<br>从Memory中恢复T/U等标量寄存器。 |
| VPAR, VSEQ；<br>MPAR, MSEQ | 需要硬件保存：<br>将BPC保存至SSR:EBPC; <br>将BARG中其余信息保存至SSR:EBARG; <br>将触发异常的Group的GroupID记录在SSR:EBARG中;<br>软件选择性保存：<br>通过调用TSTORE指令将所有或某一类Tile寄存器保存至内存；<br>通过调用ESAVE模版块保存Group的TPC和LPR至Tile寄存器; <br>通过调用TSTORE指令将ESAVE输出的Tile寄存器内容保存至内存。 | 需要硬件恢复：<br>从SSR:EBPC中恢复BPC；<br>从SSR:EBARG恢复BARG；<br>软件选择性恢复：<br>通过调用TLOAD指令从内存加载LPR等至Tile寄存器。<br>通过调用ERCOV模版块恢复Group的状态；<br>通过调用TLOAD指令从内存中加载回Tile寄存器内容。|

**1.2.2增加系统寄存器**

新版本中，增加一组系统寄存器，用于硬件在主动产生异常和被动产生中断时，将异常地址、块指令内部状态以及块类型等存储起来，并更新触发这次硬件更新的块类型。异常或中断处理完成后，再从这组寄存器恢复。

EBPC和ETPC等：

| SSR_ID | 寄存器 | 位宽 | 描述 |
|--------|---------|------|------|
| 0xnf0b | EBPC | 64 | 用于记录发生异常的块指令BPC以及BPCN_OFFSET。 |
| 0xnf0c | EBARG | 64 | 用于保存发生异常的块指令的跳转方式、块类型以及输出寄存器等参数。 |
| 0xnf0d | ETPC | 64 | 用于记录发生异常的微指令TPC。 |
| 0xnf0e | EBPCN | 64 | 用于记录发生异常的块指令下个块的BPC。 |

其中，EBPC寄存器的格式定义如下：
 
![ebpc](../figs/isa/version/0.55/ebpc.png)

EBARG寄存器的格式定义如下：

![ebarg](../figs/isa/version/0.55/ebarg.png)

ETPC寄存器的格式定义如下：

![etpc](../figs/isa/version/0.55/etpc.png)

EBPCN寄存器的格式定义如下：

![ebpcn](../figs/isa/version/0.55/ebpcn.png)

**1.2.3 增加ESAVE和ERCOV模版块**

如上面1.2.1所述，当VPAR/VSEQ/MPAR/MSEQ等Tile块发生异常或中断时，软件可以调用ESAVE模版块来保存块内的LPR内容到Tile寄存器中。异常恢复时，再通过调用ERCOV模版块从Tile寄存器中恢复块内寄存器的状态。

这两个模版块定义如下：

异常保存块-ESAVE 用于 向量数据块 或 访存数据块 执行过程中遇到异常或中断时，保存块内所有的上下文到指定的Tile寄存器中。ESAVE是一条多输出指令，其中：

- 第一个输出Tile寄存器用于保存异常块块内的私有寄存器，包括LB/LC寄存器、标量寄存器、向量寄存器、掩码寄存器等等等。
- 其他输出Tile寄存器用于保存异常块自身的输出Tile的内容。

当前版本，由于向量数据块和访存Tile块最多可以有4个输出Tile寄存器，因此ESAVE指令最多可以有5个输出Tile寄存器。

汇编格式：`ESAVE , ->DstTile0<32KB>, DstTile1<32KB>, ..., DstTile4<32KB>`

异常恢复块-ERCOV 用于 向量数据块或访存数据块 异常或中断处理完成后，从指定的Tile寄存器中恢复块内所有的上下文状态。

ERCOV是一条多输入指令，其中：

- 第一个输入Tile寄存器用于恢复异常块块内的私有寄存器，包括LB/LC寄存器、标量寄存器、向量寄存器、掩码寄存器等。
- 其他输入Tile寄存器用于恢复异常块自身的输出Tile寄存器内容。

与ESAVE指令的输出Tile数量匹配，当前版本ERCOV指令最多有5个输入Tile寄存器。
汇编格式：`ERCOV SrcTile0, SrcTile1, ..., SrcTile4`

BSTART.TEPL块指令的编码如下：
 
![bstart.tepl](../figs/isa/version/0.55/bstart.tepl.png)

Function字段编码映射表:

| Function | TileOp | 说明 |
|----------|--------|--------|
| 0-29 | RESERVE | 保留 |
| 30 | **ESAVE** | 异常保存块，用于保存发生异常的Tile块的块内状态。 |
| 31 | **ERCOV** | 异常恢复块，用于恢复发生异常的Tile块的块内状态。默认带有可继承属性，后序块指令可继承本块的内部状态。 |

### 1.3 异常处理

**1.3.1异常**

异常是在指令流水线中被同步检测到的事件。这种事件通常在逻辑上导致流水线无法继续（比如指令的要求无法被满足），必须立即转移到其他指令序列上。
异常可以同步发生在指令的执行中间，这个过程指令的部分行为可能已经生效，也可能未生效，也可能全部生效。具体情况和具体的指令和异常的类型相关。如果没有专门说明，默认特定指令发生了异常，则指令要求的所有行为都不生效，异常指令指针也仍停留在发生异常的指令上。

灵犀指令集支持块头指令和块体指令的精确异常。无论是块头指令还是块体指令异常，异常块指令指针EBPC总是指向发生异常的块指令BSTART，ETPC总是指向异常指令的地址。如果是块体指令异常，处理器需要将异常状态寄存器ECSTATE_ACRn.BI（BI表示BlockInner）置为1；相反，如果是块头指令异常，需要将异常状态寄存器ECSTATE_ACRn.BI设置为0。软件可通过BI信息决定是否保存和恢复异常块的块内状态。

特殊注意：

- 如果异常发生在块中间，硬件必须保证异常块内部的所有寄存器内容保留且资源不释放。从而保证软件可以通过一个新块（例如ESAVE模版块）来保存异常块的内部状态。
- CUBE块执行过程中不支持产生异常。
- TMA块内部不支持产生异常。

**1.3.2 增加块指令异常类型**

当触发了调度时，为了内核（ACR1）能够判断用户态是否使用了VECTOR或CUBE类型块指令，从而进行对应的上下文保存以及调度。当前版本增加了如下的控制机制：

- 内核（ACR1）初始化时，配置SCONFIG_ACR1寄存器中异常使能位为1；
- 当用户态（ACR2）进程使用VECTOR或CUBE类型块指令时，触发相应异常陷入ACR1，异常码TRAPNUM=0，CAUSE=4。内核进行相应的处理：
    * 配置ECONFIG_ACR1寄存器中不同块类型的异常使能位为0，确保后续用户态使用VECTOR和CUBE指令不会触发异常；
    * 记录当前进程使用过VECTOR和CUBE标记TIF_VECTOR/TIF_CUBE；
    * 分配VECTOR和CUBE块上下文保存地址空间。
- 后续用户态再次陷入到内核时（中断或其他异常），如果触发了调度，内核检查prev进程TIF_VECTOR/TIF_CUBE标记，如果设置了，内核保存prev进程上下文。

上述仅用于简单说明VECTOR或CUBE块指令的异常处理方式，具体实现过程内核可进行调整设计。

增加异常种类如下：

| 陷入代号（TrapNum） | 原因代号（Cause） | 异常参数代号 |  触发指令 |
|---------------------|-----------------|-------------|---------------|
| E_INST(0) | E_PEREM(4) | 0 | MPAR/MSEQ/VPAR/VSEQ |
|           |            | 1 | CUBE |

注意：ECONFIG寄存器由IENABLE寄存器修改而来，在IENABLE原有字段的基础上增加V和C标志位，作为VCETOR和CUBE指令的异常使能位。

寄存器格式：

![econfig](../figs/isa/version/0.55/econfig.png)

**1.3.3 状态迁移**

操作系统OS对Janus Core不同处理单元进行上下文切换（Context Switch）的方案设计如下：

* **BCC Context Switch**
    * 上下文保存：
        1. 保存EBARG至内存Memory
        2. 如果context switch发生在块体，保存LPR至内存	
    * 上下文恢复：
        1. 从内存中恢复EBARG
        2. 如果context switch发生在块体，恢复块内LPR的状态
        3. 执行ACRE指令（如果context switch发生在块体，ACRE参数必须是1。
* **VECTOR/MTC Context Switch**
    * 上下文保存：
        1. 保存EBARG至内存Memory
        2. 如果context switch发生在块体，保存LPR至内存:
            1. 如果需要，则保存所有Tile寄存器到内存：TSTORE T#1~T#8, U#1~U#8, M#1~M#8, N#1~N#8；
            2. 通过ESAVE保存LPR至Tile寄存器，然后通过TSTORE保存该Tile寄存器至内存	
    * 上下文恢复：
        1. 如果context switch发生在块体，从内存中恢复LPR:
            1. 通过TLOAD加载LPR内容至Tile寄存器，然后通过ERCOV恢复LPR的状态；
            1. 如果需要，从内存恢复所有Tile寄存器内容：TLOAD T#1~T#8；TLOAD U#1~U#8；TLOAD M#1~M#8；TLOAD N#1~N#8；
        1. 从内存中恢复EBARG；
        2. 执行ACRE指令（如果context switch发生在块体，ACRE参数必须是1。）
* **CUBE Context Switch for ACC** 
    * 上下文保存：
        1. 拷贝ACC寄存器内容至通用Tile寄存器：ACCCVT ACC, ->dstTile；
        2. 保存该Tile寄存器内容至内存中：TSTORE srcTile；	
    * 上下文恢复：
        1. 通过TLOAD指令从内存中恢复Tile寄存器内容；示例：TLOAD ->T
        2. 通过BSTART.VPAR块构造主对角线为1的矩阵（单位矩阵）；示例：VPAR ->T
        3. 通过MAMULB指令恢复ACC寄存器的内容。示例：MAMULB T#2, T#1, ->ACC

### **1.4特权级（ACR）切换**

ACR切换允许由灵犀核（LxLC）的内部或外部请求主动触发，请求来源分为异常、中断、系统调用块指令、ACRC和ACRE微指令等。

* 异常，系统切换到目标ACR状态。主要用于被管理的软件把灵犀核(LxLC)的控制权还给管理软件。其中ACRC指令属于块体微指令。
* 中断包括外部中断（EI）和Timer中断（TI）
* ACRE微指令，仅在系统块内生效，该指令提交会立即提交当前块并进入目标ACR。主要用于管理软件把灵犀核(LxLC)控制权主动交给被管理的软件。
* 系统调用块，块调用时系统切换到目标ACR状态，块提交后恢复到切换前的ACR。主要用于关键跨特权级请求的高效调用。

**1.4.1 SERVICE_REQUEST**

SERVICE_REQUEST只能被异常或中断驱动，异常都是同步的，称为SYNC_SERVICE_REQUEST。中断是异步的，称为ASYNC_SERVICE_REQUEST。
SYNC_SERVICE_REQUEST和ASYNC_SERVICE_REQUEST在灵犀指令集架构中统称陷阱，进入陷阱的过程，称为陷入。SERVICE_REQUEST流程如下：

对于任意从ACRn到ACRm的SERVICE_REQUEST，其具体行为为:

* 如果是浮点运算产生的相关异常，设置CSTATE.flags中的对应标志位。
* 当前SSR:CSTATE保存到SSR:ECSTATE_ACRm，如果触发指令是块头指令，设置SSR:ECSTATE_ACRm.BI为0，否则设置为1；
* 异常块的BPC保存至EBPC_ACRm;
* 异常块的BARG内容保存到EBARG_ACRm，设置EBARG_ACRm.BlockType为触发块类型。
* 如果异常块是STD、SYS或FP块，保存触发异常指令的TPC到ETPC； 
* 如果异常块是MPAR或VPAR块，保存触发异常的GroupID至EBARG的GroupID字段。
* CSTATE.I设置为0；            # 中断使能位
* CSTATE.ACR位置为m；
* BARG复位到初值；
* BPC设置为EVBASE_ACRm；
* 对于SYNC_SERVICE_REQUEST：
    * TRAPNO_ACRm.E置1；      # 同步异常标志位
    * 根据陷入代号和参数，设置SSR:TRAPNO_ACRm和SSR:TRAPARG0_ACRm。
* 对于ASYNC_SERVICE_REQUEST：
    * TRAPNO_ACRm.E置0；
    * 根据中断类型设置SSR:TRAPNO_ACRm和SSR:TRAPARG0_ACRm。
以上行为在灵犀逻辑核(LxLC)内部一次完成，中间不会有其他改变灵犀逻辑核(LxLC)状态的行为介入。

**1.4.2 ACR_ENTER**

ACR_ENTER通过ACRE指令请求，并在指令提交的时候激发。对于一次从ACRn发起的ACR_ENTER，其具体过程为：

* 灵犀逻辑核(LxLC)的ACR状态切换到系统寄存器ECSTATE_ACRn.ACR。目标ACR必须和当前ACRn可比，并且 ACRn p>= ECSTATE_ACRn.ACR。否则这个步骤本身触发E_INST(EC_PARAM)异常;
* 用SSR:ECSTATE_ACRn的内容恢复当前SSR:CSTATE的状态;
* 用SSR:EBPC_ACRn恢复BPC的内容，并调度BPC所在的块执行;
* 根据ACRE.RRA参数，选择是否用SSR:EBARG_ACRn的内容恢复BARG。
* 如果EBARG中记录的块类型是STD、SYS或FP，用SSR:ETPC_ACRn的内容恢复TPC执行；

### **1.5 部分系统寄存器的修改**

为了适配现有异常处理流程的设计，部分系统寄存器有整体删除以及部分字段的修改。

1.5.1 删除CSTATE寄存器的ebv位

修改前：

![cstate](../figs/isa/version/0.55/cstate_old.png)

修改后：

![cstate](../figs/isa/version/0.55/cstate_new.png)

**1.5.2 修改ECSTATE的ebv位**

ECSTATE的ebv位改为BI，用于标识异常块服务请求SERVICE_REQUEST是否发生在块中间。如果发生在块体内则此位被置1，否则清除。

修改前：
 
![ecstate](../figs/isa/version/0.55/ecstate_old.png)

修改后：
 
![ecstate](../figs/isa/version/0.55/ecstate_new.png)

软件可根据ECSTATE的BI位是否置位，决定是否保存以及恢复块内状态。

**1.5.3 删除TRAPNO的BI标志位**

与ECSTATE中的BI定义重复，因此删除。

![trapno](../figs/isa/version/0.55/trapno_old.png)

修改后：

![trapno](../figs/isa/version/0.55/trapno_new.png)

**1.5.4 删除ELINK和EBSTATEP寄存器**

原有设计中，ELINK用于发生异常服务请求SERVICE_REQUEST处理时，保存异常块的BPC。而EBSTATEP则用于存储EBSTATE的内存指针。新的设计下，异常块的BPC改为保存至EBPC中，因此删除ELINK。而EBSTATE一部分保存到寄存器中另一部分软件自己决定是否保存，而不是统一存到内存里，因此删除EBSTATEP。

![ssr](../figs/isa/version/0.55/ssr.png)

### 1.6 更新ACRC和ACRE指令定义

**1.6.1 acrc执行语义加强定义**

新版本中，acrc执行语义修改为：立即提交当前块并发起一次系统请求，请求类型通过request_type参数指定。其他定义无改动。

约束：acrc指令是一条带有BSTOP语义的指令，因此其必须作为所在块指令的最后一条微指令。

本指令触发系统请求后，与普通异常处理相同，硬件保存acrc所在块的BPC至EBPC以及acrc的TPC至ETPC。那么在返回到用户态前：

- 软件如果不做修改，将返回到原acrc的地址处，重新发起一次系统请求。（redo syscall）
- 如果期望返回到acrc下一条指令继续执行，那么软件需要将EBPC和ETPC内的地址改为ETPC原值加4（即acrc的指令长度）。

示例：
```asm
    BSTART.SYS        <--- BPC
    B.ATTR TRAP
    ldi [a0, 8], ->t
    ldi [a0, 16], ->t
    mul t#1, t#2, ->t
    acrc SCT_SYS      <--- TPC
    BSTART.STD      <--- NextBPC       
    ...
```

ACRC触发系统调用后如何继续执行的方式说明如下：

| 异常保存寄存器（SSR） | 硬件保存的内容 | 软件不修改，重新发起请求 | 软件修改，从ACRC的下个指令继续执行 |
|----------------------|--------------|-------------------------|---------------------------------|
| EBPC | BPC | BPC | TPC+4 |
| ETPC | TPC | TPC | TPC+4 |

**1.6.2 acre指令修改**

acre指令用于设置当前块的ACR切换要求，立即提交当前块并执行ACR_ENTER流程，把当前ARC切换为目标ACR。目标ACR由执行acre指令所在特权级的ECSTATE寄存器指定。
acre指令带有一个Return Request Argument参数，简称RRA，该参数用于指定异常提交时的状态。

指令汇编：`acre RRA_Type`

当前版本，RRA_Type的取值范围包括：

- RRAT_DEFAULT(0)：BSTATE在提交的时候复位为默认状态。
- RRAT_RESTORE(1)：用EBSTATE初始化BSTATE。
- 其他值保留，如果执行时遇到其他值，提交时触发非法指令异常。

修改点：删除RRA_Type为2时的RRAT_REDO_ECALL类型。软件可通过修改EBPC和ETPC的值执行REDO_ECALL操作。

注意事项：

- 本指令提交后，当前块指令将立即提交。因此本指令必须作为所在块指令的最后一条微指令。
- acre所在块指令是可继承的，后序块指令可继承本块的内部状态。

acre使用示例：
```asm
# 异常恢复时特权态：
ERCOV                        <- 恢复异常块的块内状态
BSTART.SYS
acre RRAT_RESTORE            <- 返回指定特权级
# 返回用户态执行BPC指示的块
BSTART.xx                      # 新块继承恢复的状态
inst                           <- 从ETPC恢复的TPC指示的指令
```

### **2.1 更新EBREAK指令**

EBREAK（Exception break）指令用于触发软件断点。本指令通过抛出 断点异常E_BREAKPOINT的方式请求调试器，并将立即数写入SSR:TRAPNO寄存器的cause字段低位。

汇编格式：`ebreak imm`

为了满足内核调试需求，新版本对ebreak指令的修订如下：

- 增加立即数参数用于内核调试，立即数的含义由内核定义。
- 删除CMT参数，与普通异常处理方式相同。
- 调整编码，修改后的指令编码见下面图示。

指令编码：

![ebreak](../figs/isa/version/0.55/ebreak.png)

### **2.2 增加C.EBREAK指令**

由于灵犀指令集中，指令最小长度是16bit。因此新版本中增加一条c.break指令，以便调试器可以安全地替换任意地址处的指令而不破坏下一条指令。

汇编格式：`c.ebreak imm`

编码格式如下:

![c.ebreak](../figs/isa/version/0.55/c.ebreak.png)

硬件执行时同样需要将立即数写入SSR:TRAPNO寄存器的cause字段低位。

### V.MOV指令

- **背景**：在控制流分支中，由于寄存器相对索引距离有限，需要一条不受全局P-Mask控制的指令实现数据全拷贝。
- **定义**：汇编格式为`v.mov SrcL.<T>, ->RegDst.<W>`，实现对输入寄存器SrcL的全拷贝，结果写入目的寄存器RegDst。
- **示例**：在else分支中使用`v.mov vt#1, ->vt`全拷贝if分支中的寄存器内容。

### MAMULBMX缩放矩阵乘法指令与微缩放机制

- **目的**：提升矩阵乘法的数值动态范围和表达能力，支持FP32精度下的近似操作或低比特宽乘法的精度补偿。
- **指令类型**：
    - **MAMULBMX**：执行缩放后的矩阵乘法，结果写入ACC寄存器。
    - **MAMULBMXAC**：执行缩放后的矩阵乘加运算，结果写入ACC寄存器。
    - **MAMULBMX.ACC**：执行缩放后的矩阵乘累加运算，结果写入ACC寄存器。
- **微缩放机制**：
    - **硬件基础**：CUBE Core的16×16×16 Tile级别矩阵乘单元，缩放单元位于Tile A和Tile B的输入乘法路径中，缩放因子存储在ScaleTileA和ScaleTileB中。
    -  **计算方式**：
       1. 对输入Tile进行逐元素缩放：
          - Tile A：`A_scaled[i][j] = A[i][j] * ScaleA[i][j]`
          - Tile B：`B_scaled[i][j] = B[i][j] * ScaleB[i][j]`
       2. 执行缩放后的矩阵乘法：`ACC[M][N] += MAMULB(A_scaled[M][K], B_scaled[K][N])`
    - **关键特性**：K维度共享缩放因子，ScaleA每行共享一个因子，ScaleB每列共享一个因子，减少存储和传输开销。

### DMA指令

- **MCOPY.D指令**：新增支持DMA拷贝的指令，硬件不支持DMA时等同于原MCOPY指令。
- **dma指令**：从源地址拷贝64字节数据到目的地址，拷贝完成后提交指令。

### FENCE指令修订

- **FENCE.D指令**：命名改为DSB。增加标记位M，M=0表示系统默认同步方式，M1表示用户自定义同步方式。
- **FENCE.I指令**：命名改为ISB。

### 增加TEPL类TileOp定义

该类TileOp统一由“BSTART.TEPL”指令开启，然后通过“Mode”和“Function”字段编码指定具体的TileOp。“BSTART.TEPL”指令的编码如下：

![bstart.tepl](../figs/isa/version/0.55/bstart.tepl.png)

新增TileOp列表如下：

| Mode | Function | TileOp | 说明 |
|------|----------|--------|------|
| 0    | 0        | TADD   | 两个Tile的逐元素加法。dst = src0 + src1 |
| 0    | 1        | TSUB   | 两个Tile的逐元素减法。dst = src0 - src1 |
| 0    | 2        | TMUL   | 两个Tile的逐元素乘法。dst = src0 * src1 |
| 0    | 3        | TDIV   | 两个Tile的逐元素除法。dst = src0 / src1 |
| 0    | 4        | TREM   | 两个Tile的逐元素余数，余数符号与除数相同。dst = remainder(src0, src1) |
| 0    | 5        | TFMOD  | 两个Tile的逐元素余数，余数符号与被除数相同。dst = fmod(src0, src1) |
| 0    | 6        | TAND   | 两个Tile的逐元素按位与。dst = src0 & src1 |
| 0    | 7        | TOR    | 两个Tile的逐元素按位或。dst = src0 | src1 |
| 0    | 8        | TXOR   | 两个Tile的逐元素按位异或。dst = src0 ^ src1 |
| 0    | 9        | TSHL   | 两个Tile的逐元素左移。dst = src0 << src1 |
| 0    | 10       | TSHR   | 两个Tile的逐元素右移。dst = src0 >> src1 |
| 0    | 11       | TMAX   | 两个Tile的逐元素最大值。dst = max(src0, src1) |
| 0    | 12       | TMIN   | 两个Tile的逐元素最小值。dst = min(src0, src1) |
| 0    | 13       | TCMP   | 比较两个Tile并写入一个打包的谓词掩码。dst = cmp.xx(src0, src1) |
| 0    | 14       | TPRELU | 带逐元素斜率Tile的逐元素参数化ReLU。dst = (src0 > 0 ? src0 : src1 * src0) |
| 0    | 15       | TABS   | Tile的逐元素绝对值。 |
| 0    | 16       | TNOT   | Tile的逐元素按位取反。 |
| 0    | 17       | TNEG   | Tile的逐元素取负。 |
| 0    | 18       | TEXP   | 逐元素指数运算。 |
| 0    | 19       | TLOG   | Tile的逐元素自然对数。 |
| 0    | 20       | TRECIP | Tile的逐元素倒数。 |
| 0    | 21       | TSQRT  | 逐元素平方根。 |
| 0    | 22       | TRSQRT | 逐元素倒数平方根。 |
| 0    | 23       | TRELU  | Tile的逐元素ReLU。dst = src0 > 0 ? src0 : 0 |
| 0    | 24       | TADDC  | 三元逐元素加法：dst = src0 + src1 + src2。 |
| 0    | 25       | TSUBC  | 三元逐元素减法：dst = src0 - src1 + src2。 |
| 0    | 26       | TSEL   | 使用掩码Tile在两个Tile之间进行选择（逐元素选择）。dst = (mask > 0 ? src0 : src1) |
| 0    | 27-31    | RESERVE| 保留 |
| 1    | 0        | TADDS  | Tile与标量的逐元素加法。 |
| 1    | 1        | TSUBS  | 从Tile中逐元素减去一个标量。 |
| 1    | 2        | TMULS  | Tile与标量的逐元素乘法。 |
| 1    | 3        | TDIVS  | 与标量的逐元素除法（Tile/标量或标量/Tile）。 |
| 1    | 4        | TREMS  | 与标量的逐元素余数。dst = remainder(src, scalar) |
| 1    | 5        | TFMODS | 与标量的逐元素余数。dst = fmod(src, scalar) |
| 1    | 6        | TANDS  | Tile与标量的逐元素按位与。 |
| 1    | 7        | TORS   | Tile与标量的逐元素按位或。 |
| 1    | 8        | TXORS  | Tile与标量的逐元素按位异或。 |
| 1    | 9        | TSHLS  | Tile按标量逐元素左移。 |
| 1    | 10       | TSHRS  | Tile按标量逐元素右移。 |
| 1    | 11       | TMAXS  | Tile与标量的逐元素最大值。 |
| 1    | 12       | TMINS  | Tile与标量的逐元素最小值。 |
| 1    | 13       | TCMPS  | 将Tile与标量逐元素比较。 |
| 1    | 14       | TLRELU | 带标量斜率的LeakyReLU。 |
| 1    | 15-23    | RESERVE| 预留编码 |
| 1    | 24       | TADDSC | 带标量融合逐元素加法运算。dst = src0 + scalar + src1。 |
| 1    | 25       | TSUBSC | 带标量融合逐元素减法运算。dst = src0 - scalar + src1。 |
| 1    | 26       | TSELS  | 使用掩码Tile在源Tile和标量之间进行选择（逐元素选择）。dst = (mask > 0 ? src0 : scalar) |
| 1    | 27       | TEXPANDS| 将标量广播到目标Tile中。 |
| 1    | 28-31    | RESERVE| 预留编码 |
| 2    | 0        | TROWSUM| 通过对列求和来归约每一行。 |
| 2    | 1        | TROWMAX| 通过取列间最大值来归约每一行。 |
| 2    | 2        | TROWMIN| 通过取列间最小值来归约每一行。 |
| 2    | 3        | TROWPROD| 通过跨列乘积来归约每一行。 |
| 2    | 4        | TROWEXPAND| 将每个源行的第一个元素广播到目标行中。 |
| 2    | 5        | TROWEXPANDADD| 行广播加法：加上一个每行标量向量。 |
| 2    | 6        | TROWEXPANDSUB| 行广播减法：从src0的每一行中减去一个每行标量向量src1。 |
| 2    | 7        | TROWEXPANDMUL| 行广播乘法：将src0的每一行乘以一个每行标量向量src1。 |
| 2    | 8        | TROWEXPANDDIV| 行广播除法：将src0的每一行除以一个每行标量向量src1。 |
| 2    | 9        | TROWEXPANDMAX| 行广播最大值：与每行标量向量取最大值。 |
| 2    | 10       | TROWEXPANDMIN| 行广播最小值：与每行标量向量取最小值。 |
| 2    | 11       | TROWEXPANDEXPDIF| 行指数差运算：计算exp(src0 - src1)，其中src1为每行标量。 |
| 2    | 11-15    | RESERVE| 预留编码 |
| 2    | 16       | TCOLSUM| 通过对行求和来归约每一列。 |
| 2    | 17       | TCOLMAX| 通过取行间最大值来归约每一列。 |
| 2    | 18       | TCOLMIN| 通过取行间最小值来归约每一列。 |
| 2    | 19       | TCOLPROD| 通过跨行乘积来归约每一列。 |
| 2    | 20       | TCOLEXPAND| 将每个源列的第一个元素广播到目标列中。 |
| 2    | 21       | TCOLEXPANDADD| 列广播加法：对每一列加上每列标量向量。 |
| 2    | 22       | TCOLEXPANDSUB| 列广播减法：从每一列中减去一个每列标量向量。 |
| 2    | 23       | TCOLEXPANDMUL| 列广播乘法：将每一列乘以一个每列标量向量。 |
| 2    | 24       | TCOLEXPANDDIV| 列广播除法：将每一列除以一个每列标量向量。 |
| 2    | 25       | TCOLEXPANDMAX| 列广播最大值：与每列标量向量取最大值。 |
| 2    | 26       | TCOLEXPANDMIN| 列广播最小值：与每列标量向量取最小值。 |
| 2    | 27       | TCOLEXPANDEXPDIF| 列指数差运算：计算exp(src0 - src1)，其中src1为每列标量。 |
| 2    | 28-31    | RESERVE| 预留编码 |
| 3    | 0-29     | RESERVE| 预留编码 |
| 3    | 30       | ESAVE  | 异常保存块，用于保存发生异常的Tile块的块内状态 |
| 3    | 31       | ERCOV  | 异常恢复块，用于恢复发生异常的Tile块的块内状态 |
