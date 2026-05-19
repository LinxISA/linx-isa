# 变换指令

变换（shuffle）指令用于并行块内的多个lane并行执行模式中，跨lane进行数据搬移，这种操作通常用来改变张量的维度顺序或元素位置。

并行块内支持4种shuffle操作：

| 模式 | 描述 | 涉及指令 |
|------|------|----------|
| **up**        | 将数据移动到更高ID的lane中（shuffle data to upper lanes） | V.SHFL.UP, V.SHFLI.UP |
| **down**      | 将数据移动到更低ID的lane中（shuffle data to lower lanes） | V.SHFL.DOWN, V.SHFLI.DOWN |
| **butterfly** | 蝶形数据交换（butterfly data exchange）                  | V.SHFL.BFLY, V.SHFLI.BFLY |
| **index**     | 获取指定lane ID的数据（absolute source lane id）         | V.SHFL.IDX, V.SHFLI.IDX |

## 指令列表

每种模式提供两条指令，分别包含一个全寄存器传参的版本和一个带立即数传参的版本，提供给软件灵活选择。

|     微指令    |         汇编格式                          |
|--------------|-------------------------------------------|
| V.SHFL.UP    | `v.shfl.up   SrcL.{T}, SrcR.{T}, SrcD.{T}, ->Dst.{W}` |
| V.SHFL.DOWN  | `v.shfl.down SrcL.{T}, SrcR.{T}, SrcD.{T}, ->Dst.{W}` |
| V.SHFL.BFLY  | `v.shfl.bfly SrcL.{T}, SrcR.{T}, SrcD.{T}, ->Dst.{W}` |
| V.SHFL.IDX   | `v.shfl.idx  SrcL.{T}, SrcR.{T}, SrcD.{T}, ->Dst.{W}` |
| V.SHFLI.UP   | `v.shfli.up   SrcL.{T}, SrcR.{T}, imm, ->Dst.{W}`     |
| V.SHFLI.DOWN | `v.shfli.down SrcL.{T}, SrcR.{T}, imm, ->Dst.{W}`     |
| V.SHFLI.BFLY | `v.shfli.bfly SrcL.{T}, SrcR.{T}, imm, ->Dst.{W}`     |
| V.SHFLI.IDX  | `v.shfli.idx  SrcL.{T}, SrcR.{T}, imm, ->Dst.{W}`     |

## 指令编码

![shuffle](../../../figs/bitfield/svg/Introduction_64bit/ShuffleVector.svg)
