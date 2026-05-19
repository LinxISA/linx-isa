# 第五章：更高效的访存子系统

作者：苏放 589498

本章主要介绍用于解决数据访存造成的流水线停顿的两种常用方法：提升访存并行度和降低访存延时。

## 提升访存并行度


  ![lsu_size](../figs/white_paper/Chapter-5/LSU.png){width="800"}


上图展示了Intel几代CPU核的load queue, store queue容量和可以并行执行的load/store指令数量。不难看出，随着乱序窗口大小的提升，访存并行度也在随之增大。更大的访存并行度有助于均摊由于缓存缺失引起的延时。

## 降低访存延时

除了访存并行度之外，访存造成的延时也是制约处理器性能提升的重要因素。即使数据在一级缓存中命中，从访存指令发出到数据被其后的依赖指令使用通常也需要经过4个周期的延时，其中包括虚实地址转换、cache索引和tag比对、store queue转发数据等操作。如果一级缓存缺失，还需要更长的延时完成数据访问。本节重点介绍几种常见的降低访存延时的方法。

### 数据预取


  ![prefetcher](../figs/white_paper/Chapter-5/prefetcher.png){width="800"}


数据预取通过预测哪些缓存行将要在近期被访问，提前将数据从下层缓存或内存中取入更上层的缓存，从而降低访存延时。从软件是否可见的角度分类，数据预取机制可分为软件预取和硬件预取两个分类。

硬件预取从最简单的连续访存(stream access)开始，逐步发展到支持较复杂的时间/空间访存特征。典型的访存特征以及对应的硬件预取机制包括：

- **连续地址(stream)/等步长序列(stride)**: 通常使用基于区域或基于PC的训练机制，记录相邻或相等步长的访问，并基于一定深度触发预取。常见的预取机制包括Stride prefetcher[[1]](https://dl.acm.org/doi/pdf/10.1145/144965.145006), Best-offset prefetcher[[2]](https://ieeexplore.ieee.org/abstract/document/7446087), AMPM prefetcher[[3]](https://dl.acm.org/doi/abs/10.1145/1542275.1542349?casa_token=kJVvH3ngHmoAAAAA:YNUx9cltafl3m6kKu0Fhpq6-FzJOtC-PEgn8RHUff6ixO8N0BBgFwCvvmnTEX6yDLfuUBJLj98EyoQ)和Signature path prefetcher[[4]](https://ieeexplore.ieee.org/abstract/document/7783763)。

- **空间关联的特征(spatial correlated pattern)**: 常见于对结构体的访问。对不同结构体的成员访问通常具有同样的规律，即一个结构体内的访存构成空间关联的特征。针对该特征的预取机制为Spatial memory streaming (SMS)[[5]](https://dl.acm.org/doi/abs/10.1145/1150019.1136508?casa_token=3cXzSZFD9jAAAAAA:F8DerWLL1jZjFY-xh_pBbNiL-JrAjUsTVTqKy3tKIZV_mmGWzbC-HISE1LPnchpsAzno2R4IKjVHtQ).

- **时间关联的特征(temporal correlated pattern)**: 时间关联的特征指时间上相邻的访存指令在一段时间后可能以相同的顺序重复出现，常见于链表或指针的访问。针对该特征的预取机制包括STMS[[6]](https://ieeexplore.ieee.org/abstract/document/5430739)，Triage[[7]](https://dl.acm.org/doi/abs/10.1145/3352460.3358300?casa_token=QOvG9_Fz_SUAAAAA:15B-Se9qzPclDlYtkQKrdYewQBBTa_gJtouZMF2JYylSNGjRXr6BuNOMtpSt52B0h5m9u2gmzBSKmg)。ARM在其Neoverse N2处理器中也引入了这一机制。

传统的软件预取只支持对一个指定地址的预取（例如ARM的PRFM指令）。使用软件预取指令需要程序员或编译器对预取的收益有较大的信心，如果预取地址错误或预取的缓存行本身已存在于L1缓存中，这条预取指令并不会提升性能，反而会引起额外的取指开销。因此，软件可见的预取机制逐渐朝着“软件提示、硬件预取”的方向演进，软件基于高层语义通过较小的指令开销给出提示，具体是否发出预取请求由硬件决定，这种软硬件协同设计的预取方式将在[下一章](Chapter-6.md)中重点介绍。

### 地址预测
理想的数据预取只能保证访存指令执行时在L1缓存命中，但L1缓存命中通常仍然需要4个周期的延时才能得到数据。地址预测技术则是继续优化4周期访存延时的一个可能手段。地址预测技术在访存指令执行之前（取指或译码阶段），通过访存指令的PC预测访存指令的虚拟地址，并提前执行访存指令。2009年，Rami Sheikh提出在取指阶段做访存地址预测，并将提前执行访存指令得到的数据用作值预测[[8]](https://dl.acm.org/doi/abs/10.1145/3123939.3123951?casa_token=p8_mNGe6IJsAAAAA:IlQxmkcy9R6-ahaPFj6G9f5cwuYWscv-UOGbZrBVcKyyEAQmpYHbHMAj-mPY-vL9aApyH-SDG6sdpg)（值预测在下一小节中将会介绍）。2022年，Intel提出寄存器预取技术(Register File Prefetching), 利用预测得到的访存地址提前将L1缓存内的数据预取到寄存器中[[9]](https://dl.acm.org/doi/abs/10.1145/3470496.3527398?casa_token=rxEEWf1tNC4AAAAA:IXCu1u1Eo4b4eKu6Uw0X5-_b8Xs0Qz2s3f-oPxBGfuLtsEXOX5oAKkkgSJQmxYb5_oTKBUaxVGm_NA)。

### 值预测
前两个小节中介绍的数据预取或地址预测技术并没有打破原有程序中的数据依赖链，依赖访存指令的计算指令仍需要等待访存指令给出结果之后才能被执行。值预测(Value prediction)能够在访存指令执行之前就把预测的数据传递给后续的依赖指令，等到访存指令真正执行时，再把真实数据与预测数据做比对，如果不同则会发生流水线冲刷。常见的值预测算法包括常值预测(last value prediction)[[10]](https://ieeexplore.ieee.org/abstract/document/807407), 等步长值预测(strided value prediction)[[11]](https://dl.acm.org/doi/abs/10.1145/859618.859656?casa_token=AZb2imHBG6IAAAAA:qella30ePZN6YhRyYTqxyA8AOyMW8bZBClQC2l8DkZuzBz3a-Cv6ZkynTjLIbCs_Q2VkfcWKKlY4RQ)以及基于Context的任意值预测(context-based value prediction)[[12]](https://ieeexplore.ieee.org/abstract/document/744311)。由于值预测机制真正打破了数据依赖，相比地址预测，能进一步缩短程序的关键路径。但使用值预测的一个挑战是可能破坏内存模型。

### 内存重命名
与值预测/地址预测不同，内存重命名(memory renaming)算法通过预测load指令和store指令的依赖关系，使load指令不必从缓存或存储器子系统中获取数据，而是直接从前一次store指令所使用的寄存器中转发数据[[13]](https://ieeexplore.ieee.org/abstract/document/645812)。内存重命名算法需要硬件预测机制在load和store指令之间建立联系，该算法在寄存器溢出(register spilling)时通常能获得显著的性能收益。
