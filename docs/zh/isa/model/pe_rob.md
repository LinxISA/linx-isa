# pe_rob

![pe_rob](../../figs/model/model_detail/pe_rob.svg "pe_rob")

## 数据结构

* **wbAluInst**
功能：作为EXE Stage的输出端暂存算术指令，并作为WB Stage的输入，承担EXE Stage到WB Stage指令通道的职能，同时作为俩个流水段间打拍的载体
实现：vector

* **wbAguInst**
功能：作为EXE Stage的输出端暂存load指令，并作为WB Stage的输入，位于将Ggpr中的地址写到Lgpr的数据流中

* **wbStaInst**
功能：作为EXE Stage的输出端暂存store(addr)指令，并作为WB Stage的输入，承担EXE Stage到WB Stage指令通道的职能，同时作为俩个流水段间打拍的载体

* **wbStdInst**
功能：作为EXE Stage的输出端暂存store(data)指令，并作为WB Stage的输入，承担EXE Stage到WB Stage指令通道的职能，同时作为俩个流水段间打拍的载体

* **wbLoadInst**
功能：接收来自LSU的load指令，并作为WB Stage的输入

* **wbBruInst**
功能：作为EXE Stage的输出端暂存分支指令，并作为WB Stage的输入，承担EXE Stage到WB Stage指令通道的职能，同时作为俩个流水段间打拍的载体

## 执行过程

1. 对于load指令，其src存在三种可能：Ggpr、Lgpr、T寄存器。当其src为Ggpr时，则需要额外进行一步操作：将计算出的地址从Ggpr中写到Lgpr。当load指令结束RF stage获得所需要访问的地址后，可以在向LSU发送req的同时，并行地进行上述的额外操作。

2. 对于store指令，需要将源寄存器中的数据写到目的地址所指向的内存中，并将目的地址写到目的T寄存器中，因此只有store(addr)需要有WB Stage，而store(data)没有WB Stage。

3. 等到rob中指令成为最老的指令后，再进行commit。
