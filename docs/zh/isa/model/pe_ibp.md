# PE Inst_BP

## 功能

1. 在往IFU发送微指令取指请求前，需要先进行微指令的分支预测

![pe_ibp](../../figs/model/model_detail/pe_ibp.svg)

## 数据结构

* **inst_bp_mode**
功能：用于决定使用何种微指令分支预测的字段：
当为1，将使用function model跑出来的指令序列作为bp的参考，即perfect bp。
当为0，则进行基于1位饱和计数器的bp,即仅根据该TPC 上一次的跳转情况决定本次的跳转
当为2，则进行基于2位饱和计数器的bp。

* **hyperTrace**
功能：存储了function model跑出来的指令序列，用于给bp mode为1时的pe提供分支指令预测结果的参考。而定位某一个块在trace中的方法是：根据到最老块的距离定位到本块在 trace中的位置。
实现：为HyperTraceEntry的结构体变量，存储了bpc、isHyper、instQ，其中instQ就是实际用于存储指令序列的队列。

* **hyperIQ**
功能：记录了最新的块内跳转地址，用于bp mode为0时的分支预测的目标地址预测。
实现：deque

* **instMap**
功能：存储了分支预测的目标地址预测值，用于bp mode为2时的分支预测的目标地址预测。
实现：unordered_map

## 执行流程

1. 当inst_bp_mode不等于1时，调用PE::checkBranchInst()，向IBP传递tpc等信息，而分支指令的目标地址预测值将通过dst字段传回pe
2. Pe将会调用IBP::predict()，并判断inst_bp_mode的值，若为0，将调用IBP::checkBranchInst()，使用hyperIQ进行基于1位饱和计数器的bp；若为2，将调用IBP::noHistBP ()，使用instMap进行基于1位饱和计数器的bp；
3. 当inst_bp_mode等于1时，pe将使用hyperTrace进行perfect bp。
