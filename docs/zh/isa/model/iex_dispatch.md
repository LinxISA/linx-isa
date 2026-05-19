# IEX Dispatch

## 功能

1. 将rename后的微指令分发至各个isq中

![iex_dispatch](../../figs/model/model_detail/iex_dispatch.svg)

## 数据结构

* pe_iex_alu_array
功能：各个PE重命名阶段发出的算术指令将先发往pe_iex_alu_array，然后再以负载均衡的策略分发至某个aluIQ中
实现：SimQueue的队列

* pe_iex_lda_array
功能：各个PE重命名阶段发出的load指令将先发往pe_iex_alu_array，然后再以负载均衡的策略分发至某个ldaIQ中
实现：SimQueue的队列

* pe_iex_sta_array
功能：各个PE重命名阶段发出的store(addr)指令将先发往pe_iex_alu_array，然后再以负载均衡的策略分发至某个staIQ中
实现：SimQueue的队列

* pe_iex_std_array
功能：各个PE重命名阶段发出的store(data)指令将先发往pe_iex_alu_array，然后再以负载均衡的策略分发至某个stdIQ中
实现：SimQueue的队列

* pe_iex_bru_array
功能：各个PE重命名阶段发出的分支指令将先发往pe_iex_alu_array，然后再以负载均衡的策略分发至某个bruIQ中
实现：SimQueue的队列

## 执行流程

1. 将调用OPE::insertToPEArray()将rename阶段后的微指令插入到各个pe_iex_q中
2. 然后再调用DispatchUnit::dispatch()将pe_iex_array中的指令以负载均衡的策略分发至某个IQ中
