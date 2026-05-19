# 块头缓存 (Block Header Cache, BHC)

块头缓存是一块用于暂存 Block Header 的一级缓存，与处理器中的 L1 Cache 一致，都是通过利用空间局部性与时间局部性来提升访存效率的硬件。由于 BFU 整体架构采用了不同于传统的耦合预测与取指的做法，故 BHC 也被作为 BTB 使用。BHC 暂不支持 Hit Under Miss, 即在遇到 Cache Miss 时，后续请求将会被阻塞。

## 块头缓存配置

* 块头缓存容量为64KB，Cacheline 粒度为64B
* Data Array 支持4 Way 组相联结构，每个 way 有8块单口 SRAM，分为4个qword，8个dword，SRAM深度为256，宽度为78bit
* Tag Array 为单口SRAM，深度为256，位宽为49bit
* 暂不支持写操作，唯一的写操作来自于Cacheline Fill
* VIPT，Virtual Index Physical Tag
* ECC检测，1-bit 错误自我更正，2-bit 错误上报异常


## DATA Array 读流程

Data Array 分为读和写两条路径。其中，写口的数据来源于 L2 缓存数据回填；读口的数据来源于 BFU 的读请求；从 Data Array 中读出数据后，会进行 ECC 判断，若出错则上报异常信号。主要处理流程如下：
* 在 I2 流水，进行数据读写准备，生成使能，地址等信号。对于写操作，数据来源为 L2 数据回填。硬件将根据回填信号生成写使能，地址，写掩码等信号。对于读操作，信号来源为BFU。硬件将根据输入的地址，计算得出读操作的数据选择和地址等信号。
* 在e1 stage，实现数据的读写操作。写数据操作时，从fill的ecc数据和data数据按顺序写入memory中；读数据时，由于一共有4个way，每个way有4个qword，每个qword包括两个dword，因此总计会读出32个数据。读数据在e2 stage被读出。
* 在e2 stage，首先每个way会根据qword_en信号，从这个way读出的8个结果数据中选出d0和d1两个数据，四个way总计选出8个数据，然后根据tag得到的way_hit信号选出某个way的d0和d1数据。
* 在e3 stage，对选出的pipe数据进行ecc_err检测，输出err信号和correct_data。


## PLRU 算法

Plru (Partial Least Recently Used) 是一种基于 lru (Least Recently Used) 的算法，本模块中采用的是 Tree-plru 算法。具体实现方式如下：
以一个 4-way 的缓存为例，需要设置3个状态位：lvl1_node，lvl2_left，lvl2_right，初始态为全0，分别与4个 Way 对应。对应情况如下图所示：

![PLRU_FIG0](../figs/uArch/PLRU0.png){ width="400" } 

当发生 Fill 操作判断替换 Way 时，首先读取 lvl1_node 的值，根据结果决定继续判断 lvl2_left 还是 lvl2_right。如果 lvl1_node 的值为0，则读取 lvl2_left 的值，忽略 lvl2_right；如果 lvl1_node 的值为1，则读取 lvl2_right 的值，忽略 lvl2_left，从而选择出替换的 Way 编号。在替换 Way 之后，三个节点的状态将被更新。除了替换操作外，当某个 Way 命中时，三个节点的状态同样需要更新。


根据以上分析可知，在初始发生 Fill 操作时，由于 lvl1_node 为0，会读取 lvl2_left 的值，而 lvl2_left 也为0，所以选取 Way0 进行写数据操作。在下一拍，由于 Way0 被写入数据，会更新三个节点的状态。更新规则如下：

	对于 lvl1_node，选择 Way0/1 时，置1，选择 Way2/3时，置0；
	对于 lvl2_left，选择 Way0 时，置1，选择 Way1时，置0，其余情况保持；
	对于 lvl2_right，选择 Way2 时，置1，选择 Way3时，置0，其余情况保持；

更新后节点状态如下:

![PLRU_FIG0](../figs/uArch/PLRU1.png){ width="400" } 
 
在此基础上发生fill操作时，会选择way2进行写数据操作，并更新节点状态。
