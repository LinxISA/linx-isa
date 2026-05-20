#  读取请求缓存 (Load Hit Queue, LDQ)

## 读取请求缓存描述

在本设计中，微架构将 LHQ 与 LMQ 合并为一个统一的 LDQ。读取请求缓存是用寄存器搭建的用于存储进入 LSU 的 Load 指令。其中包括：

* L1 Cache Hit 的 Load 请求
* L1 Cache Miss 的 Load 请求
* TLB Miss 的 Load 请求

## 数据结构

|域段 | 位宽 | 描述|
|----|----|----|
|vld | 1 | 有效位|
|peid| 2 | 执行引擎 ID|
|bid | 7 |Block ID|
|rid | 7 | PE ROB ID|
|size| 3 | total size|
|pa_page1|36| PA1[47:12]|
|va_idx1|14|VA1[13:0]|
|pa_page2|36|PA2[47:12]，当 Load 指令跨页表时存在|
|va_idx2|14|PA2[13:0]，当 Load 指令非对齐时存在|
|tlb_hit1| 1| TLB hit1|
|tlb_hit2| 1|TLB hit2, 跨页表时存在|
|hit1_vld|1|DCache hit1|
|hit1_way|2|DCache hit1 way|
|hit2_vld|1|DCache hit2，当 Load 指令跨 Cacheline 或页表时存在|
|hit2_way|2|DCache hit2 way，当 Load 指令跨 Cacheline 或页表时存在|
|fault_vld|1|fault|
|size|2|Load 数据大小，0:1B, 1:2B, 2:4B, 3:8B|
|ma_type|2|指令非对齐类型，0: 对齐, 1: 跨8B/16B, 2: 跨64B, 3: 跨页表|
|bm1| 8| 指令返回数据8字节中哪些字节有效|
|bm2| 8| 指令返回数据8字节中哪些字节有效，非对齐时存在|
|sign|1|指令是否是读有符号数|
|ldq_fsm| 4| LDQ FSM|
|total|194| |
 
## LDQ 操作

1、	每个时钟周期，LDQ 将为 PE 输入的 Load 指令分配一个空闲表项用于存储指令信息，来自 PE 的 Load 指令将和 LDQ 重新选取的指令仲裁。其中 LDQ 重新选取的优先级更高。对于非对齐的 Load 指令需要存入 LDQ 后重新选取执行
2、	每个时钟周期，LDQ 将挑选出一个最老的 TLB Miss 或 L1 DCache Miss 的表项用于重新选择 (Repick)，来自 PE 的 Load 指令和 LDQ 中未获取 TLB 或 DC TAG 的 Load 指令将一起发送到 TLB 和 L1 DCache 仲裁
3、	ODU分发的LOAD指令在L0_TLB和L1 DC仲裁失败（TAG或DATA）时需写入LDQ等待repick重新发起L0_TLB和L1 DC仲裁；
4、	M2仲裁出结果后向STQ、SCB发送data forwarding请求，与STQ、SCB中地址匹配确认是否有数据满足data forwarding；
5、	L1 DC miss的话需要向L2请求数据，等待L2返回数据后更新LDQ状态重新发起L1 DC查找；
6、	Load UOP和某个STQ PA CAM Match，但是有多个STQ和当前Load UOP地址Match，发起计数等待计数结束后重新repick这个load指令。
7、	TLB命中、L1 DC命中且LOAD数据返回后对应的LDQ entry状态机跳转到resolve状态并发送load resolve到ROB通知LOAD执行完毕；
8、	ODU输入STORE指令会查询LDQ，当发生younger resolved load 在older store 前完成时，LSU 判别发生了ordering violation，LDQ发送nuke指示到ROB来触发nuke flush；
9、	接收ROB发送的commit指令后，轮询BID和RID，把load resolve且older的entry释放；
10、	接收ROB发送的FLUSH指令后，flush比flush bid/rid younger的entry；

LDQ的数据结构如下：

由于是RAM搭建的预测表，对预测带宽和端口要求比较高，所以有一定预测瓶颈和面积代价。性能的评估需要灵犀核那边负责，
