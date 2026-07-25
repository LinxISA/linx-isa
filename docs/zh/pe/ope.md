#	OPE

**注意：微架构相关问题优先咨询 朱凡 00370308**<span style="background-color:#facccc;"></span>

这一章节主要描述了 OPE 的整体架构。OPE 全称为 Out-of-Order Process Engine。其作为一个可执行 灵犀指令集 微指令的小核，拥有独立的取指，解码，计算，访存单元，使其可独立完成标准块微指令的执行，其中包括：ALU指令、L/S指令、GET/SET指令等。其与以下外部模块有交互：

|模块|描述|
|--|--|
| **L2 Cache**| 负责与 OPE 中 L1 I/DCache 交互填充数据|
| **BCC OOO** | 提供给 OPE 一系列块层面的必要信息，如：重命名信息，Block PC，Block ROB 的块追踪信息等|
| **LSU** | 负责处理来自 OPE 的访存的请求|

<span style="background-color:#facccc;">【注意】通常情况下LSU是CPU中的一部分，但在此架构文档中，我们将LSU独立出来单独描述</span>

## 架构框图
结构框图

![架构细节图](../figs/uArch/OPE_BLK.PNG){ width="800" }

架构细节图

![架构细节图](../figs/uArch/OPE_TOP.PNG){ width="800" }



## 模块介绍
**OPE** 大致的可以分为以下几个模块

### IFU ingress

OPE 不再定义第二套嵌套 IFU。core-level IFU 唯一拥有解耦 I-SIDE/B-SIDE
架构。I-SIDE 把完整 64-bit 指令写入 Instruction Buffer，D1 每周期读取
最多四条并完成完整译码。OPE 接收 D1/D2/D3 group 原子接纳后的
decoded/renamed uop；它不接收块头后再从 micro-PC 重新取四条指令。

规范见 [LinxCore IFU 架构](../architecture/linxcore/ifu.md)。

### DEC 与 DISP
**DEC** 是 core D1/D2 decode-group 路径。D1 对四条固定 64-bit 指令做
完整译码；D2 计算资源需求和 boundary ownership。

**DISP** 只接收 D3 原子接纳后的 uop，并路由到对应 issue structure；
它不重复取指或预测。

### PE ROB

**ROB** 利用了结构化指令集特有的分块机制，从而使能硬件可以同时挖取程序执行时两个维度的并行度，即块间并行度（Block Parallelism）与块内并行度（Instruction Parallelism）。同时确保了块的乱序发射，和块内微指令在乱序发射时程序的精确状态与正确性。

其中 PE ROB 存在于 OPE 内部，其只需要保证块内的提交顺序，而块间的提交顺序将交由上级的块ROB保证。通过以链表的形式实现 PE ROB，使其可以同时提交来自不同块的最老微指令，从而达到乱序提交的效果，并且不会影响架构状态的精确性。同时，由于指令不需要按序提交，微指令ROB硬件资源可以提前释放，就意味着ROB的投机深度比实际深度更大，从而释放了更大的并行度。

具体细节，请参考[Block ISA ROB方案](https://codehub-y.huawei.com/Graphflow/blockisa-doc/docs/backend/files?ref=master&filePath=docs%2Fbackend%2Frob.md&isFile=true)

### ISQ
**ISQ** (Issue Queue) 作为发射单元队列，存储了 DISP 发下来的微指令。队列中记录了每条指令的发射状态与信息，其中包括了操作数是否准备完成，指令类型等信息。

在ISQ微架构中，有四个类型的管道：
 
 | 管道|描述 |
 |--|--|
 |ALU0 ISQ|ALU0 计算管道，负责处理计算，逻辑，移位等基础功能
 |ALU1 ISQ| ALU1 计算管道，负责处理计算，逻辑，移位等基础功能
 |LSU  ISQ|LSU  访存管道，负责处理内存的读写请求
|GSU  ISQ|GSU  外部交互管道，负责 GET/SET/SETBPC/SETC 等需要用到GPR, BPC等外部寄存器的指令

### RF
**RF** (Register File) 为一个64深64宽的寄存器堆，包含有8个读口4个写口。指令将通过读口读取其所需的操作数，并通过写口将指令的计算的结果写入相应的物理寄存器。为了加速指令的执行，微架构在操作数读出后会将其与来自 WriteBack 流水的结果进行仲裁，从而达到转发的效果。

### EXE
**EXE** （Excution Unit）包含有若干个计算器件，囊括了所有 灵犀指令集 中定义的计算类型。与 ISQ 对应的，EXE 也拥有四条计算管道，每条管道负责的计算已在 ISQ 的章节中概括。 同样的，在 EXE 的起始也会经过转发网络获取来自WriteBack 流水的计算结果。
