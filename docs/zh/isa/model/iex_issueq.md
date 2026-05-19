# IEX Issue Queue

## 功能

1. 将iq中的指令发射进入select数组中，下一拍进入RF stage，结束后写入exe数组中。

![iex_iq](../../figs/model/model_detail/iex_iq.svg)

## 数据结构

* **aluIQ**
功能：即算术指令的iq，有6个
实现：vector

* **ldaIQ**
功能：即load指令的iq，有4个

* **staIQ** 
功能：即store(addr)指令的iq，有4个

* **stdIQ** 
功能：即store(data)指令的iq，有4个

* **bruIQ**
功能：即分支指令的iq，有4个

* **selectAluInst**
功能：作为aluIQ的输出端暂存aluIQ中选中并发射的算术指令，同时作为RF stage的输入端
实现：vector

* **selectAguInst** 
功能：作为aluIQ的输出端暂存aluIQ中选中并发射的load指令，同时作为RF stage的输入端

* **selectStaInst** 
功能：作为aluIQ的输出端暂存aluIQ中选中并发射的store(addr)指令，同时作为RF stage的输入端

* **selectStdInst** 
功能：作为aluIQ的输出端暂存aluIQ中选中并发射的store(data)指令，同时作为RF stage的输入端

* **selectBruInst**
功能：作为aluIQ的输出端暂存aluIQ中选中并发射的分支指令，同时作为RF stage的输入端

* **exeAluInst**
功能：作为RF stage的输出端暂存算术指令，并作为EXE Stage的输入，承担RF stage到EXE Stage指令通道的职能，同时作为俩个流水段间打拍的载体
实现：vector

* **exeAguInst**
功能：作为RF stage的输出端暂存load指令，并作为EXE Stage的输入，承担RF stage到EXE Stage指令通道的职能，同时作为俩个流水段间打拍的载体

* **exeStaInst**
功能：作为RF stage的输出端暂存store(addr)指令，并作为EXE Stage的输入，承担RF stage到EXE Stage指令通道的职能，同时作为俩个流水段间打拍的载体

* **exeStdInst**
功能：作为RF stage的输出端暂存store(data)指令，并作为EXE Stage的输入，承担RF stage到EXE Stage指令通道的职能，同时作为俩个流水段间打拍的载体

* **exeBruInst**
功能：作为RF stage的输出端暂存分支指令，并作为EXE Stage的输入，承担RF stage到EXE Stage指令通道的职能，同时作为俩个流水段间打拍的载体

## 执行过程

* 调用issue函数，发射IQ中的指令，将其中的指令select到对应的select数组中。
* 有**5类IQ**，每类IQ中包含多个发射队列；
* 有**5类select**数组，每类select数组也包含多个数组；
* 每类select数组与一类 IQ 相对应，此类IQ的指令只能进入相对应的那一类select数组中，每个IQ一拍发一条指令，没有就绪指令的IQ就不发。
