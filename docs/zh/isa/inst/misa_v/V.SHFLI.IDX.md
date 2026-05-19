# V.SHFLI.IDX

## 说明

跨通道·索引搬移(*Shuffle by Index with Immediate*)<br>
将`源通道SrcLane`内源寄存器中的数据搬移到`当前通道CurLane`的目的寄存器中。源通道的ID由索引值与shuffle范围计算得到。

## 汇编语法

```asm
    v.shfli.idx SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, imm, ->RegDst.{W}
```

## 汇编符号

- **SrcL**：存储shuffle源数据的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：存储shuffle范围的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **imm**：表达shuffle索引值的立即数，范围是[16383, 0]。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。

## 编码格式

![V.SHFLI.IDX](../../../figs/bitfield/svg/Instruction_64bit/V.SHFLI.IDX.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
integer {m, srcwidth0} = DecodeINT(SrcL);
integer {n, srcwidth1} = DecodeINT(SrcR);
integer {d, dstwidth} = DecodeDst(RegDst);

bits(srcwidth1) range = V[n, srcwidth1];
if range == 0 then range = Groupsize;
bits(64) pmask = P;   // lane掩码
bits(64) index = ZeroExtend(imm) % range;

// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer src_id = laneid / range * range + index;    // 源数据所在lane的ID

    bits(srcwidth0) data = V[m, srcwidth0, src_id];  //lane[src_id]对应的SrcL值
    V[d, dstwidth, laneid] = data;
}
```

![shfl.idx](../../../figs/isa/inst/shfl.idx.png)

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
