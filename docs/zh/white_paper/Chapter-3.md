# 第三章：并行度与粒度

作者：周若愚 532827

不同指令集架构的CPU在处理计算的粒度是不相同的，下图展示的是一个通用的计算会被拆成约9种不同的粒度。在不同层级粒度下表达的程序即可获取相应层级的并行度。


  ![bpu](../figs/white_paper/Chapter-3/best_instr.png){ width="800" }


理论上说，每个粒度层级上都可以构建成一种层次化调度模型。下面我们就列举一下各个层级的调度实体：

- **进程**：调度实体为操作系统
- **线程**：调度实体为操作系统或者硬件线程
- **函数**：Function Flow Task Scheduler/Runtime 根据粒度，可以为软件调度或者硬化的调度器
- **SCF**: Structured Control Flow 是BlockISA概念中自创的粒度，这个后续会展开
- **异常点**：调度粒度在Reorder Buffer
- **微指令**：调度粒度在Issue Queue或者Reservation Station

在这些粒度中，容易被忽略的两种粒度为**SCF**和**异常点**：

## Structured Control Flow:

指的是一种Single-Entry-Single-Exit的代码形态。SCF代表着一种一段代码集合，内部有一系列跳转。但是SCF对于跳转预测器来说，只要Entry是Taken的，那么其Exit就一定是Taken的。Exit代表的是跳转的汇聚点。SCF本质上代表的是控制流图中比跳转粒度更高的一个集合。Yale Patt对这种形态成为[Wish Branch](https://ieeexplore.ieee.org/document/1540947), 编译器上称作[Structured Control Flow](https://medium.com/leaningtech/solving-the-structured-control-flow-problem-once-and-for-all-5123117b1ee2)。

SCF理论奠定了WebAssembly指令集的设计基础。

## Exception Point:

CPU会以会产生异常/Flush的点为分界线，将指令流重新组合成Reorder Buffer Group。在CPU和整系统看来，基于ROB Group的指令粒度才是最优的指令粒度。因为如果指令流内部不会产生异常和Flush，那么CPU也不需要为一个ROB Group内部保留架构状态。

## 指令并行度 Instruction-Level Parallelism

ARMv8指令集共有1070条指令，53种格式，6千页的指令mannual。x86也拥有1300多条指令。龙芯架构提出了更多的指令，将多种指令集融合在一起。但是这些指令中，大多数是为了针对一些特定场景而设计的复合指令。但是如果把这些指令拆成微码，无非就是简单的运算，内存读写，compare，branch复合在一起而已。如果只表达微码，使用统一的压缩格式，那么我们设计的指令集反而非常简单。

将各式各样运算拆成最细的微指令，这些微指令由于足够细，可以做到在通用运算，专用运算，各种场景下的复用，因为大家本质上都是这些基本运算。如果拆的不细，那么这些运算和指令就不能复用。这样就会造成了指令集的分裂。就像DNA/RNA都可以分解成A, T, C, G碱基序列。所有各种各样的蛋白质都可以分解成20种氨基酸一样。我们把任何指令拆成了这些微码，就可以在微码级别做到复杂指令的复用。

从第一性原理的角度来看，任何通用运算都可以被分解成基础微指令。CPU最终是在这些微指令上获取的并行度。但是目前的物理实现是无法直接将指令流打碎了在一个层级上去大量地细粒度调度这些的微码指令。但是只把运算拆到最碎后，损失了原本软件系统的组织结构信息的。CPU依然是需要维护原来的语义的情况下进行层次化调度，将这些拆散的微指令又能够合成一个整体来执行。

因此我们希望通过块指令描述这些微指令的组织结构，范围，连接关系，并行度等等。这些信息通过块指令ISA传递给微架构。组织信息例如一种模板，把这些微指令构建成复杂复合指令，向量运算，微线程运算等等。每种微架构处理这种组织信息的方式不同，但是给的信息是足够让这些微指令在微架构中被优化到最优。硬件根据模板去合并Fusion，这其实和ARM/x86指令集设计一千多条指令的效果相同。

## 访存并行度 Memory-Level Parallelism



## 块并行度 Block Parallelism

在BlockISA指令集中，我们定义了一种新型指令粒度，成为块粒度。其中块的定义为一系列指令序列，这些指令序列需要遵循**Single-Entry-Single-Exit**的语义, 也就是上述所描述的SCF粒度。


  ![bpu](../figs/white_paper/Chapter-3/block_header.png){ width="800" }


编译器将这些指令序列总体的对外输入，输出，Exit跳转提取出来后，构建成一个header。

基于这种抽象出来的程序，就统一由Block Header组成，如下图所示。


  ![bpu](../figs/white_paper/Chapter-3/block_header.png){ width="800" }


由于Block Header格式固定，可被专用的硬件进行高效调度和投机执行。我们通过Block粒度构建双层次调度模块，可以有效降低CPU的实现复杂度。通过低成本实现更大指令窗口，获取更高的性能收益。

在层次化调度下，最终的块并行度还是会被拆解成微指令并行度。因此块并行度并没有本质上要求源程序提升并行度，而是要求源程序需要按照层次化的写法进行重新编译。如下图所示，BlockISA使能的层次化调度：


  ![bpu](../figs/white_paper/Chapter-3/sch_unit.png){ width="800" }


## 函数并行度 Function Parallelism

在Function Flow的中，我们定义了一种新型的函数定义。其中Function代表的是一种无状态或者有状态的任务。

(未完待续)
