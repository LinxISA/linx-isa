# 第二章：CPU架构历史演进：经验与教训

早在 1978 年，16bit 的 Intel 8086 处理器就已经商用。同时，标准 In Order 五级流水的微控制器也已经非常成熟。在 80 到 90 年代演进的十年里，众多处理器核指令集架构诞生又沉寂。1990 年到 2000 年左右可以称为指令集架构的黄金年代，各类执行模型、并行模型以及 IR 格式定义都非常活跃。这些指令集，例如 MIPS、HP 的 PA-RISC、DEC 的 VAX 及其后续 Alpha、Sun 的 SPARC、VLIW、Itanium、Open-RISC、IBM 的 PowerPC 等，并非全部在技术上落后，只是在商业上并不都成功。ISA 历史反复说明，最终留下来的架构往往不仅取决于技术优劣，也受到经济、市场和生态规模的强烈影响。指令集上的百花齐放也为二进制转码和编译器技术带来了巨大机遇。直到多核时代出现之后，主流指令集才逐渐收敛到 x86 和 ARM 两大阵营。新的 RISC-V 指令集如果抓不住新兴市场和新型应用，也同样很难撼动既有架构的地位。

如果我们重温历史，再次回顾这些指令集背后的设计理念和技术细节，发现他们也是在当时的市场，芯片制程，软件生态，应用场景上找到的最优解。每一个玩家都是在当时的情势下选择的对自己成本最低和利益最大化的选择。对于图灵来说，我们需要通过本白皮书传达出来我们对这些历史上架构的看法和观点。

在本章，我们尝试去捋顺过往架构的技术亮点和优缺点，把握各个架构所提倡的主张，并猜测为什么最后在商业上失败。对于学术界上的架构设计，我们也同时给出为什么无法商业化的主要原因。

## RISC处理器的演进

### IBM的Power架构
PowerPC的根源是IBM 801，它是最早的基于RISC的处理器之一。 PowerPC未能在市场普及很大的原因是开放不足。Power架构的处理器以及软件栈授权费价格过高。对于用户来说，使用Power的处理器在软件开发，运维成本要远高于x86处理器和arm处理器。软件上的限制导致了处理器的性能没有那么重要。虽然IBM在2013年成立了OpenPOWER基金会，宣布将PowerISA开源。但是市场上并没有一款免费的或者廉价liscence的IP可使用。另外SOC层级来看，其他指令集的CPU是难以融入以AMBA为首的围绕ARM CPU构建的总线协议生态。

 从上面来看，Power架构的失败，并不是其指令集和处理器微架构设计的技术不先进。更大程度上是价格贵，软件生态小，用户基数少和商业模式的失败。
 
### DEC的VEC指令集以及之后的Alpha指令集
DEC是计算机业界最老牌的公司，但是由于商业模式在21世纪时被分拆。其中VEC指令集是在70到80年代开发的32位CISC指令集。90年代Alpha是64位RISC指令集。基于Alpha开发的21064系列处理器也成为1993年性能最高的CPU处理器。这个处理器的架构被众多大学作为超标量处理器的教材。很多学术界在超标量处理器上研究的微架构技术，都在商业版的Alpha上成为现实。同时也培养出来大量的体系结构架构师，在DEC分拆后分散到Intel和AMD中。

在技术上，Alpha的RISC指令集开发时间最早。当时为了超越x86的单线程性能和降低面积，Alpha采用了比ARM还要更弱的内存序模型。Alpha指令集目前设计比RISC-V还要精简，但这是以软件复杂性的提升为代价的。Alpha指令集专利过期后被开源，现在被用于中国的神威超算/申威处理器。但是基于申威处理器的编程依然非常困难，因此限制了软件生态的发展。编程困难的主要场景在于单线程的data-barrier的使用，以及多线程多核之间的cache一致性设计上的薄弱。

### SUN的SPARC指令集架构

SPARC全称Scalable ProcessorArchitecture - 可扩展式处理器架构。SPARC架构至今还存活，虽然SUN公司已经不复存在。但是SPARC架构依然以自己独特的多线程优势依然存活在服务器市场。日本的Fujitsu是SPARC架构目前主要商用的场景。SPARC在设计之初，就以精简指令集+Throughput Computing的理念来设计的。这和其母公司Sun的基因有关。SUN更偏向以软件为角度设计处理器，基于Solaris操作系统进行软硬件协同优化。

SPARC架构的Register Window的设计，是希望通过对寄存器分组来降低状态迁移的开销。这个理念也影响到后续Itanium的设计，以及我司一些架构在降低Context Switch的尝试。但是这种设计对于编译器和软件开发的门槛略高。在Sparc上开发出高效的并行代码需要的软件成本还是过高。

SPARC架构以UntraSPARC T1的[Niagara架构](http://arsenalfc.stanford.edu/kunle/publications/niagara_micro.pdf)为起点，开创了一个CPU核8线程的先锋，朝着Throughput Computing的目标走到了极致。直到目前为止，高并发多线程处理器依然是数据库，网络报文转发，DPU相关应用上的处理器形态。

### Intel的Itanium

与其他架构不同的是，[Intel的安腾架构](https://ieeexplore.ieee.org/document/877946)失败大部分都归咎于技术路线上的失败。安腾架构是基于VLIW (Very Long Instruction Word)这个理念构建的指令集架构。之后Intel和HP联合开发，将VLIW改进到显式并行指令架构(Explicitly Parallel Instruction Computing-EPIC)。 EPIC允许处理器根据编译器的调度并行执行指令而不用增加硬件复杂度。乱序执行的硬件开销都被推给了编译器和汇编程序员来调度。

然而这种基于确定性调度的计算架构注定是失败的。同时，EPIC的设计理念尝试避免从本文第一章提到的“图灵税”，并没有做到架构与微架构的高效解耦。不同版本的EPIC处理器需要重新编译软件才能获取新的硬件性能。这样造成了极高的软件开发开销。另外EPIC指令集并没有解决单线程处理器的核心问题：更聪明的投机执行和更高效的前后端子系统。降低指令间依赖关系检查的复杂度占整个CPU处理器的复杂度占比很低。

在细节设计上，EPIC指令集采用了和x86完全不同的MMU设计，巨大的寄存器文件和虚拟化设计，导致基于在EPIC上设计和[实现操作系统的复杂性](https://www.usenix.org/legacy/publications/library/proceedings/usenix05/tech/general/gray/gray.pdf)。

!!! note "观点"

	依赖软件和编译器提供显式表达并行度的思路并没有错误。但是软件的优势在于识别静态和全局的依赖关系信息。硬件的优势在于处理动态的事件的信息和调度。但是对于EPIC指令集，采用了本末导致的设计理念。要求编译器来识别动态的信息，导致软件上的巨大复杂度。但是Itanium提出了对编译器的高水平要求激发了编译器领域的长足发展。

## 数据流架构的演进

在80年代CISC如日中天，RISC快速跟进的年代。学术界的重点在数据流架构和并行计算上。数据流架构指的是将CPU指令操作数从寄存器修改成指令之间的依赖关系图。这种指令依赖图在定义上分为了

静态数据流架构：指令个数上限为N，数据流图存在指令Buffer上，编译器需要将指令的位置排布好才能计算
动态数据流架构：指令个数无上限，数据流图存在内存上。硬件需要在一个窗口内的数据流分配Token，代表数据在图中的流动。
 
其中静态数据流结合控制流变演进成了[EGDE指令集](https://www.cs.utexas.edu/users/cart/trips/publications/computer04.pdf) （Explicit Dataflow Graph Execution）。其核心点在于将一系列的指令按照block的形式执行，block内部以指令间的依赖关系图表达，而block外部依然按照传统的跳转的方式来表达。

另外动态数据流架构演进出来[Tagged-Token Dataflow Architecture](https://ieeexplore.ieee.org/document/48862)和[Machester Dataflow Machine](https://courses.cs.washington.edu/courses/csep548/05sp/gurd-cacm85-prototype.pdf)。其原理在于对被激活的数据流结点分配有限的token。并通过不断回收和分配token完成对整个数据流图的遍历和并行计算。

值得注意的是动态数据流架构在1990年左右就消失殆尽，并没有商用化。其核心的原因在于纯数据流的指令集架构是无法高效表达和处理具有控制属性的程序的。1990年代的超标量处理器，采用了Tumasulo的算法实现，在Reservation Station里就将传统RISC指令流实际已经在微架构内部翻译成了指令的数据流图，获得了微架构的性能提升。因此可以这样说，超标量在不改变指令前端的情况下，依然可以获得动态数据流架构的性能优势。超标量通过Reorder Buffer维护了精准的架构状态。但是如果动态数据流架构增加token维护了精确的架构状态，那么它的形态和现有的超标量处理器形态是相同的。动态数据流的token的概念，和超标量处理器里面的Physical RF Tag有异曲同工之处。超标量的Tag Matching的复杂度在目前制程下最高也就做到一拍10个左右，这样也同时限制了动态数据流的scale up的能力。

!!! note "投机执行的收益大于数据流的收益"

	动态数据流不如超标量的另外一点就是无法高效执行投机执行。超标量处理器通过对跳转和数据做到预测，即可将最少的代码取进流水线并高效执行(预测部分子图执行)。但是对于数据流架构来说，整个图必须完整取进来才能正确完成运算，并将错误的分支给mask掉。有了投机执行后，数据流图的计算就过于臃肿，最终损失性能。这个原理和CPU支持predicate execution类似。

对于EDGE处理器来说，每个块就是一个微指令依赖图，表达图本来就需要更多信息，导致程序二进制大小扩张，由于90年代Program Memory成本过高，不利于商业上的扩展。EDGE的每条微指令用destination编码，需要处理过大扇出等极端场景，导致code size进一步增高。EDGE指令集在处理中断，debug，系统支持上难度较大。块内的指令并行度本来就不高，但是EDGE编码给块内预留了过多硬件资源，因此不得不靠编译器合并block来获取性能提升。

## 线程投机处理器架构的演进

[线程投机执行的处理器](https://www.eecg.utoronto.ca/~steffan/papers/isca00.pdf)(Thread-Level Speculation)在超标量处理器同期在学术界被广泛研究。其核心理念就是将一段单线程程序拆分成多段小线程并在一个处理器核上乐观并发执行。其获取性能的主要受益来源在于线程间并行度(Thread-Level Speculation)。


  ![bpu](../figs/white_paper/Chapter-2/thread_level_speculation.png){ width="800" }


1995年Wisconsin大学的[MultiScalar](https://dl.acm.org/doi/10.1145/225830.224451)基于上述理念，在指令集上增加tag标记，将一段程序封装成一个Task分布在不同的执行单元上执行。使能多个程序段以Round-Robin的Task-Level的粒度进行并发执行。然而Task粒度过高后，需要保存的投机状态也过高。每个线程的Load/Store都要被缓存在Address Resolution Buffer中 （ARB）。后续ARB的实现变为了Multi-Scalar的瓶颈，基于这个设计，后续的研究也激发了事务性内存的研究。

MultiScalar奠基了后续研究朝着两个方向演进，一个是朝着**更大粒度的线程并行投机执行处理器**演进，一个是朝着**适当粒度的块(Block, Trace, Slice, Strand, Chain）的粒度**去演进。前者的处理器形态变成了多个Tile的小核完成单线程程序，后者则变成了多个Lane执行共享前端和后端的Clustered CPU形态。

在1997年，[Trace Procesor](https://dl.acm.org/doi/10.5555/266800.266814) 提出依赖硬件识别出一系列基本块合成一个Trace。Trace Processor将不同的Trace提前并投机执行。Trace里面拥有自己的私有寄存器和共享寄存器概念。但是Trace是微架构自动产生，在产生Trace时需要极高的复杂度。在同一年，高光荣的学生提出来[SuperStrand Processor](http://citeseerx.ist.psu.edu/viewdoc/download;jsessionid=06DA5CA62D91967A5526D48883F1A77E?doi=10.1.1.56.4234&rep=rep1&type=pdf),其中Strand的概念被定义为一个DAG(Direct Acyclic Graph)。Strand只有等到输入都到达时才能去执行。但是DAG的自由度还是过高，后续的工作将Strand重新定义为了一条Chain，也就是指令的链条。

指令链条的定义便成为指令并行度约为1的相对独立的指令序列。指令链条具有优良的属性，例如投机的中间态小，数据局部性优异，整个链条可以在一个简单的单元上反复执行。[Dynamic Strand](https://www.microarch.org/micro37/papers/02_Sassone-DynamicStrands.pdf)提出来微架构可以通过Rename算法识别出来指令链条。后续的指令链条识别的工作被应用到商用处理器的Dispatch单元上。当然Dynamic Strand架构也倡议使用Strand Cache来缓存构建出来的指令链条。

2004年[Dependency Chain Clustered Architecture](https://cseweb.ucsd.edu/~calder/papers/IPDPS-05-DCP.pdf)发现这些指令Chain的长度过短，导致整体收益并不高。因此此工作将一部分指令进行复制，通过重复计算来降低链条间的通讯，并显著提升链条的长度。Mutlu和Patt也在同一时期提出来[Runahead Execution](https://people.inf.ethz.ch/omutlu/pub/mutlu_hpca03.pdf), 本质上实现了两个不同的执行单元。让一个执行单元预先计算出来Runhead Chain, 并将结果写入Runahead Cache中，并被真正计算的执行单元来使用。

2008年[Braid Core](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4556711)依赖修改指令集和编译器，将上述想法汇总，提出了Braid的概念。但是Braid不再以提升性能为首要目标，而是更加倾向于降低CPU实现的复杂度以及功耗上。Braid提出使用多个In Order CPU达成一个大核CPU的想法和构想。

在2008-2018年期间，**多个Lane执行共享前端和后端的Clustered CPU**形态一直不被企业界看好。主要原因是Clustered CPU并不能给单核CPU带来显著的性能收益。同时制程上的不断演进情况下，单核CPU遇到的复杂度/功耗问题都能够基本被制程和物理上的优化解决。单核CPU的性能可以通过增加Cache，增加BTB，Prefetch算法等获取足够多的单线程收益。

因此，最近几年的学术界工作都专注在将Cluster CPU Lane异构化，Master Slave化：也就是走Helper-Thread路线，或者Helper Slice路线。在不影响主流水线的过程中，帮助Prefetch和Hard-to-Predict Branch高效执行。

## Tile处理器架构的演进

Tile Processor定义为将相同的小核通过NOC一种特定互联的方式有机组合起来。在2000年左右，并行多线程程序并没有被软件所接受，因此学术界依然投入在用多核处理器来加速单线程程序。例如斯坦福的[Hydra CMP](http://arsenalfc.stanford.edu/kunle/publications/hydra_MICRO00.pdf), 尝试将单线程MIPS程序拆成线程片段，并将不同的线程片段放置在不同的CPU核上执行。线程之间投机的状态在L2 Cache层级实现冲突检查和数据通讯。

2004年左右，学术界在将小核合并成大核的热度还是很高的。MIT提出来[RAW处理器](http://groups.csail.mit.edu/commit/papers/04/raw_isca_2004.pdf)，将In Order小核阵列组合在一起，完成一个单线程程序的运算。RAW的优点和缺点也非常明显，需要依赖于编译器对指令序列进行排布。基于RAW ISA, Tile处理器的位置暴露给了编译器。编译器为了提升最终性能，需要针对RAW的拓扑结构对指令进行静态调度。依赖编译器对指令位置进行静态调度，本质上和VLIW的理念相同，对编译器提供了更高的要求。这种对编译器的强限制基本是不友好的。2004年密歇根提出的[Voltron处理器](https://courses.cs.washington.edu/courses/cse591n/09au/Papers/004-zhong.pdf)，通过对现有的CPU核增加额外的逻辑单元，实现了四个小核合并成一个大核的设计，通过使能Thread-Level Speculation和Core Fusion跑通一个单线程程序。2007年的[Composable Lightweight Processor](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4408270&tag=1)基于TRIPS处理器进行了扩展，做到了单线程和多线程程序的灵活切换。

更极端的工作在编译器的自动并行化领域，例如[Decoupled Software Pipelining](https://liberty.princeton.edu/Publications/pact04_dswp.pdf)技术完全依赖编译器，将单线程程序拆解成相互独立的Task。这些Task可以按照流水线的方式并行做计算。虽然说这些工作做了很久，但是编译器基本还是无法自动拆解单线程程序到多线程。之后的一部分工作在和事务性内存整合在一起。另一部分的工作就是倡议软件生态重新构建一种[新型的编程模型](https://liberty.princeton.edu/Publications/micro08_scale.pdf)，完全依靠编程模型和程序员，显式地把程序逻辑表达成图的形式。 但是结果往往事与愿违，软件市场总会去选择更易用，软件能够复用，具有兼容性的硬件形态。这就进一步阻碍了TLS硬件的商用。

!!! note "TLS前途如何"

	Thread-Level Speculation-TLS的思想还是很先进的。但是面临几个严重的问题，阻碍了thread-level speculation技术的进一步商业化。首先，软件业务通过多核CPU将完全并行的程序（Embarrasingly Parallel的程序）和更高维度的线程/进程/算法业务级别的并行度使用更低成本即可获取。软件通过OpenMP/MPI框架即可在更高层面的并行度上迅速获取线性Scale收益。

	对于TLS来说，由于是单个线程拆分出来的程序片段，其并行度是有限制的。对于并行度不高的单线程程序，即使拆分成多个线程，这些收益依然是不高的。因此TLS在最终获取并行度的收益上并不会带来类似于多核/GPU一样成倍的性能收益, 因而也支持不了硬件在SOC层级要更加更加复杂的协议或者事务性内存(HTM)等等。

	但是TLS这条路不能放弃，剩下两条可行的路线为：1.提升TLS的粒度到Task/Function，依赖动态系统和编程框架修改线程的语义，使其变成一种无状态的函数。通过对函数的分布式调度来进一步提升性能，同时降低硬件实现的复杂度。2.降低TLS的粒度到Block/Slice/Strand, 在不改编程框架下，通过修改指令集来吸收TLS的收益。

学术界对TLS和投机执行架构依然没有放弃。直到2015年，MIT推出来的[Swarm架构](https://people.csail.mit.edu/sanchez/papers/2015.swarm.micro.pdf)，主张的就是对单线程程序的更极致的投机执行。其主要的原因是目前部分单线程程序中依然具有巨量的不规则并行度，无法通过简单的多核并行或者编程语言框架来获取。这种**不规则并行度**，常常出现在动态规划、BackTrace, 和Nested Kernel中。目前为止，无论是CPU，还是GFU都无法高效执行这种类型的计算。
