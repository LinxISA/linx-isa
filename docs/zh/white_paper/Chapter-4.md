# 第四章：更聪明的预测和投机执行

作者：苏放 589498

!!! note "介绍"

    在一个流水线处理器中，一条指令的平均执行时间(CPI)由处理器自身结构引起的停顿、控制流引起的停顿和数据访存造成的停顿三部分组成。由于后两者对CPI有着不可忽视的贡献，一味地堆积资源实现更深、更宽的流水线并不能线性地提升性能。

本章着重讨论如何通过更聪明的预测和投机执行，降低控制流引起的停顿。第五章将重点介绍如何通过访存系统的设计和优化，降低数据访存造成的停顿。

一条分支指令会引发控制流依赖，在流水线处理器中，这个依赖通常需要在多个周期之后才能得以解除，在控制流依赖解除之前，处理器将无法决定接下来的取指路径，这会在流水线中造成大量的空泡。为了降低这种控制流引起的等待，高性能处理器通常采用分支预测+投机执行的机制，在控制依赖解除之前，投机地在分支预测器指示的路径上继续执行，从而提升指令级的并行度。

如果处理器能够保证永远在正确的路径上投机执行，那么由于程序的控制流引起的流水线停顿可以被完全消除。但由于错误的投机执行会引起流水线的冲刷，投机执行的效率受到分支预测准确率的制约。特别地，随着处理器发射宽度和流水线深度的不断增长，由于错误投机引起的流水线冲刷代价也在随之增大。因此，如何提升分支预测准确率成为了计算机体系结构领域的一个恒久话题。从1984年的基于2比特饱和计数器的动态分支预测机制[[1]](https://www.computer.org/csdl/magazine/co/1984/01/01658927/13rRUy3gmUL)，到结合全局分支历史和分支指令PC信息的gshare预测器[[2]](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.626.4268&rep=rep1&type=pdf), 再到现代处理器中的TAGE预测器[[3]](https://hal.inria.fr/hal-03408381/)和perceptron预测器[[4]](https://ieeexplore.ieee.org/abstract/document/903263/)，分支预测器已经成为CPU中最复杂的子系统之一。在现代超标量处理器中，虽然分支预测的准确率可达99%或更高，但分支预测并不是一个已被解决的问题。Intel的研究显示，基于skylake微架构，优化分支预测带来的性能收益空间可达到18.5%，如果将处理器的深度和宽度各自加倍，这个收益能达到55.3%[[5]](https://ieeexplore.ieee.org/abstract/document/9042108)。在本章中，我们从分支方向预测和跳转目标预测两个方面探讨如何实现更聪明、更准确的预测机制。

## 方向预测 Direction Prediction
继续提升分支预测器的准确率需要攻克少数“难以预测的分支(hard-to-predict branches，简称H2P分支)”，这些分支无法被TAGE或perceptron预测器准确预测。H2P分支可能来源于数据依赖、变化的函数输入或动态的的循环边界等原因[[6]](https://ieeexplore.ieee.org/abstract/document/5452016)。着力于解决H2P分支的相关工作可分为以下四个类别。

### 降低预测错误的代价
这类工作不以提升分支预测的准确率为主要目标，而是试图降低预测错误的代价。2007年，Intel和NCSU的研究者提出将分支预测失败后需要冲刷的指令分为有控制依赖(control-dependent, CD)和无控制依赖(control-independent, CI)两类[[7]](https://dl.acm.org/doi/abs/10.1145/1273440.1250717?casa_token=Xw0DRE4jKcYAAAAA:WmRpAGj6Gw0fFkXTEN7sJtscbEnhMybmhUithGLjLk38Qal3MY2A7HEPNk5py27nJnucA8IrMAkvtQ)，其中后者在分支预测错误之后存在无需冲刷的机会。进一步，CI的指令又可以根据是否与CD区域内的指令有数据依赖，进一步分为有数据依赖(control-independent-data-dependent, CIDD)和无数据依赖(control-independent-data-independent, CIDI)两类。由于CIDI指令与错误预测的分支指令及受影响的路径完全无关，在分支预测失败时，这些指令无需被冲刷或重新执行。而CIDD指令需要在分支预测错误后使用正确路径上的数据依赖重新执行。检测CI指令可以由硬件自动完成[[8]](https://ieeexplore.ieee.org/abstract/document/1410082)或基于编译器显式给出CIDI指令的范围[[9]](https://dl.acm.org/doi/abs/10.1145/3466752.3480045?casa_token=ftyU0dXu0yAAAAAA:YrJ-2QeyNUgiZ8nJK-7NhR3Ep31rx0u5xjlDzr-9DnFdVOyU92miWSETMB4v7YPf2YdMW4bbrqzuaQ)。

### 辅助预测器
这类工作通过发掘H2P分支的内在特征，实现domain-specific预测器，作为主预测器的辅助预测器。实际上，现代CPU分支预测子系统中常见的返回地址栈(Return-address-stack, RAS)和循环预测器(Loop predictor)就采用了这种思路。对于更一般的H2P分支（例如分支方向依赖load结果），北卡罗莱纳州立大学的Eric Rotenberg研究组提出了一种基于访存地址和分支方向相关性的预测器[[10]](https://people.engr.ncsu.edu/ericro/publications/conference_CF-7.pdf)，该工作能够动态地将访存地址和分支预测方向建立联系，并在随后发现这种联系时覆盖基础分支预测器（如TAGE）的预测结果。检测分支方向与访存地址相关性的任务也可以交给编译器完成[[11]](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.718.4740&rep=rep1&type=pdf). 类似地，[[12]](https://repositories.lib.utexas.edu/handle/2152/23191)提出寻找分支方向与访存的值之间的依赖关系，并借助该种依赖关系作出比基础预测器更准确的预测。

### 提前执行分支
与辅助预测器不同，该类别的方法寻求提前执行H2P分支，得到准确的分支方向。2012年，北卡罗来纳州立大学的Rami Sheikh提出Control-flow decoupling机制，在编译时把循环中的H2P分支提取出来提前计算[[13]](https://ieeexplore.ieee.org/abstract/document/6493631)。该机制需要在架构状态中新增一个分支结果队列(branch queue), 并在ISA中新增指令支持对该队列的读和写。类似地，[[14]](https://dl.acm.org/doi/abs/10.1145/3466752.3480053?casa_token=-7M2BDCrb48AAAAA:q3SomUqKgyrexky4VxsdxtREd6R0Z1T19OSAJluEI8ZVeW3_tkPLoLH0q43QwAWquDYh_dXWCXd3Rw)[[15]](https://arxiv.org/pdf/2009.09064.pdf)寻求以软件不可见的方式提前执行H2P分支，这些方法会付出更大的硬件开销。

### 消除分支
最后一类方法通过断言执行(predicated execution)的方法，将控制流转换为数据流，从而彻底消除难以预测的分支。并非对所有的H2P分支使用断言执行都能提升性能。由于断言执行需要对分支的两条路径都进行计算，这会引入额外的流水线占用。因此，如何根据分支两侧的指令数、分支的预测失败率和流水线冲刷代价等因素，估计何时使用断言执行，是该方法中的一个重要技术问题。2006年，UT Austin的Hyesoon Kim提出Diverge-Merge Processor[[16]](https://ieeexplore.ieee.org/abstract/document/4041835), 借助编译器标记出一些可能的H2P分支，在动态执行时由硬件选择是否进行断言执行。2020年，Intel进一步将标记H2P分支的工作实现在硬件中，在没有编译器的参与下，也能智能地选择何时进行断言执行[[17]](https://ieeexplore.ieee.org/abstract/document/9138936)。

## 目标预测 Target Prediction
除方向预测之外，分支预测器还提供对于跳转目标的预测，实现这一功能的结构通常称为BTB (branch target buffer)。更理想的BTB不但能降低错误的目标预测，从而减少流水线冲刷；还能够在解耦的前端结构(FDIP)中使指令预取更加准确。但是，由于软件复杂度的增速远高于硬件性能的增速，现代程序的工作集(working set)已远超指令缓存和BTB所能支撑的容量。尤其是在服务器、数据中心领域，BTB的容量已显得捉襟见肘[[18]](https://dl.acm.org/doi/abs/10.1145/3470496.3527430?casa_token=ewg698X3hroAAAAA:8oDbxY9H-UF3j9T3C-gDxxbjYVsMEYxl9rLQxRcbzPts8PwqDAws8NWHljVaW-WF_74J1L9aIsaWmg)。如上图，近年来各个厂商的CPU中BTB的容量都有着显著增大的趋势。但即使如此，由于BTB的访问在分支预测的关键路径上，BTB的容量不能无限增长。解决BTB容量不足问题的工作有以下两类：

### 次级BTB缓存
2009年，Andreas Moshovos提出借用L2 cache的部分way记录BTB的缺失历史[[19]](https://dl.acm.org/doi/abs/10.1145/1508284.1508281?casa_token=RsN4EBuum2gAAAAA:O2pHuJ2wWZT5EXaRgFkRvvv9hhgU-oHwi9m_pVzd-k2HTuRyf4MxUI57GZVDqZfBUrJWh0JR2JXaJQ)。该方法的主要优点是无须增加额外的存储空间，但也会面临与指令缓存、数据缓存争抢L2容量的问题。2013年，IBM在其z12大型机设计中引入了专用的L2 BTB[[20]](https://ieeexplore.ieee.org/abstract/document/6522308)，硬件选取合适的时机向L1 BTB进行批量预填充(bulk preload)。这个设计一直沿用到2020年的z15处理器中。

### BTB预取
预取是在不显著增大面积开销的前提下，增大有效BTB容量的一个常用手段。2017年，爱丁堡大学的Boris Grot提出一种无须添加额外存储就能实现BTB预取的机制[[21]](https://ieeexplore.ieee.org/abstract/document/7920850)。该方法在指令缓存行被预取到L1指令缓存时，提前解析其中的跳转指令和跳转目标，并预填充到BTB中。2021年，密西根大学的研究者面向数据中心应用提出基于软件的BTB预取机制[[22]](https://dl.acm.org/doi/abs/10.1145/3466752.3480124?casa_token=QK4N7xRRucMAAAAA:NcFO0-wdWmN28yjF8KFzGzThv17ojAFzIL82gJu_MRpzFQ-vQXOyCA1pLRvw4N8fENmolVHFu1ailQ)，该方法面临的主要挑战是需要在指令集中添加BTB预取指令。

## BlockISA如何使能更高效的预测器

传统指令集在支持选择性流水线冲刷时，通常需要重排序缓冲区(Reorder buffer, ROB)支持以指令为粒度的插入或删除操作。得益于层次化的指令集设计，BlockISA在支持选择性指令冲刷时只需以块为粒度冲刷或重新执行，大幅降低了ROB的硬件复杂度。

另一方面，由于BlockISA在块头指令(header)层面集中地表达控制流，无需借助传统指令集中预取指令+提前译码的方法进行BTB的预填充，而是直接从程序的块头指令段中预取BTB内容，容易实现更高效率的BTB预填充。
