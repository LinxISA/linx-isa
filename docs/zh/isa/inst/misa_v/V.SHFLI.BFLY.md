# V.SHFLI.BFLY

## 说明

跨通道·蝶型搬移(*Butterfly Shuffle with Immediate*)<br>
将`源通道SrcLane`内源寄存器中的数据搬移到`当前通道CurLane`的目的寄存器中。源通道的ID由当前通道ID与一个掩码异或计算得到。

## 汇编语法

```asm
    v.shfli.bfly SrcL<.reuse>.{T}, imm, ->RegDst.{W}
```

## 汇编符号

- **SrcL**：存储shuffle源数据的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **imm**：表达shuffle掩码的立即数，范围是[16383, 0]。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。

## 编码格式

![V.SHFLI.BFLY](../../../figs/bitfield/svg/Instruction_64bit/V.SHFLI.BFLY.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
integer {m, srcwidth} = DecodeINT(SrcL);
integer {d, dstwidth} = DecodeDst(RegDst);

bits(64) mask = ZeroExtend(imm);
bits(64) pmask = P;   // lane掩码

// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer src_id = laneid ^ mask;    // 源数据所在lane的ID

    bits(srcwidth) data = V[m, srcwidth, src_id];  //lane[src_id]对应的SrcL值
    V[d, dstwidth, laneid] = data;
}
```

![shfl.bfly](../../../figs/isa/inst/shfl.bfly.png)

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
