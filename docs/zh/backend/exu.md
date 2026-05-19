# 执行单元

指令在发出后将进入执行单元，其包含三个(或多个)流水级：寄存器读取 (RF), 数据转发 (BY), 计算 (EX)。其中计算根据指令的不同可为一个或多个时钟周期。

## 数据

在 PE 内部，所有指令的结果都将被存储在 PE 寄存器堆中。所有指令的源操作数都来自于 BPC Buffer，块寄存器堆 与 PE 寄存器堆中。其详细结构在下列章节中描述：

* [块寄存器堆](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/bcc/brf/)

* [PE寄存器堆](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/backend/pe_rf/)

## 运算

在 灵犀指令集 中，指令被分为了三类：访存类 (LSU)、计算类 (ALU)、对外通信及PC运算类 (GSU)。我们针对每个类型都有一条或多条特定的计算单元。计算完成后，结果将在寄存后在 WriteBack 流水发往寄存器堆写入目的寄存器并参与转发

此章节我们将把计算分为两个部分，包括：

* [整数运算](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/backend/exu_int/)

* [浮点运算](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/backend/exu_fp/)

## 结构框图

![AGE_MATRIX1](../figs/uArch/EXU_TOP.png){ width="800" }
