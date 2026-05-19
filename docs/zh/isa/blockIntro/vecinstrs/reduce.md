# 归约指令

在SIMT（Single Instruction, Multiple Threads）架构中，reduce是一种常用的操作，用于将多个lane计算的结果合并为一个结果。

并行块的多个lane同时执行相同的指令，但每个lane处理不同的数据。当需要将多个lane的计算结果合并为一个结果时，就需要使用reduce操作。

具体而言，reduce操作通常涉及以下步骤：

1. 将每个lane计算的结果存储在并行块内私有T,U,M,N寄存器中。
2. 对不同lane中对应的私有寄存器的结果进行归约操作，例如求和、求最大值、求最小值等。
3. 将归约结果存储在某个全局寄存器中，以便其他块指令可以访问。

![reduce](../../../figs/intro/reduce.png){ width = "800" }

因此reduce指令有如下限制：

- 不同lane中的reduce操作是无序的。
- reduce指令的结果可以输出到全局寄存器或者块内的标量寄存器T或者U中。
- 当reduce到全局寄存器，是将reduce的结果累积到全局寄存器而不是直接写入。

通过reduce操作，可以高效地合并多个lane的计算结果，从而提高并行计算的效率。在许多并行计算任务中，reduce操作都是必不可少的一步。

## 指令列表

|     微指令    |         汇编格式         |     描述                             |
|--------------|--------------------------|--------------------------------------|
| V.RDADD   | `v.rdadd SrcL.{T}, ->Dst.d`   |  将当前Group的所有有效lane中SrcL.{T}中的整数相加，结果写到Dst寄存器中  |
| V.RDAND   | `v.rdand SrcL.{T}, ->Dst.d`   |  将当前Group的所有有效lane中SrcL.{T}中的值按位与，结果写到寄存器Dst中。  |
| V.RDOR    | `v.rdor  SrcL.{T}, ->Dst.d`   |  将当前Group的所有有效lane中SrcL.{T}中的值按位或，结果写到寄存器Dst中。  |
| V.RDXOR   | `v.rdxor  SrcL.{T}, ->Dst.d`  |  将当前Group的所有有效lane中SrcL.{T}中的值按位异或，结果写到寄存器Dst中。  |
| V.RDFADD  | `v.rdfadd SrcL.{T}, ->Dst.d`  |  将当前Group的所有有效lane中SrcL.{T}中的浮点数相加，结果写到寄存器Dst中  |
| V.RDMAX   | `v.rdmaxu SrcL.{T}, ->Dst.d`  |  比较当前Group的所有有效lane中SrcL.{T}的整数，将最大值写到寄存器Dst中。  |
| V.RDMIN   | `v.rdminu SrcL.{T}, ->Dst.d`  |  比较当前Group的所有有效lane中SrcL.{T}的整数，将最小值写到寄存器Dst中。  |
| V.RDFMAX  | `v.rdfmax SrcL.{T}, ->Dst.d`  |  比较当前Group的所有有效lane中SrcL.{T}中的浮点数，将最大值写到寄存器Dst中。  |
| V.RDFMIN  | `v.rdfmin SrcL.{T}, ->Dst.d`  |  比较当前Group的所有有效lane中SrcL.{T}中的浮点数，将最小值写到寄存器Dst中。  |

## 指令编码

![Reduce](../../../figs/bitfield/svg/Introduction_64bit/ReduceOperationwithRegisterVector.svg)
