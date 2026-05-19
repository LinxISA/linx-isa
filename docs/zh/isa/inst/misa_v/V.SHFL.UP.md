# V.SHFL.UP

## 说明

跨通道·向上搬移(*Shuffle Up*)<br>
将`源通道SrcLane`内源寄存器中的数据搬移到`当前通道CurLane`的目的寄存器中。源通道的ID由当前通道ID减去偏移值计算得到。

## 汇编语法

```asm
    v.shfl.up SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, SrcP<.reuse>.{T}, ->RegDst.{W}
```

## 汇编符号

- **SrcL**：存储shuffle源数据的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：存储shuffle范围的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcP**：存储shuffle偏移量的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。

## 编码格式

![V.SHFL.UP](../../../figs/bitfield/svg/Instruction_64bit/V.SHFL.UP.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
integer {m, srcwidth0} = DecodeINT(SrcL);
integer {n, srcwidth1} = DecodeINT(SrcR);
integer {k, srcwidth2} = DecodeINT(SrcP);
integer {d, dstwidth} = DecodeDst(RegDst);

bits(srcwidth0) data;
bits(srcwidth1) range = V[n, srcwidth1];
bits(srcwidth2) offset = V[k, srcwidth2];

if range == 0 then range = Groupsize;

bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
integer delt = offset % range;

for (laneid = 0; laneid < lanenum; laneid++)
{
    integer src_id = laneid - delt;    // 源数据所在lane的ID

    if ((laneid % range) - delt) >= 0 then
        data = V[m, srcwidth0, src_id];  //lane[src_id]对应的SrcL值
    else
        data = V[m, srcwidth0, laneid];  //lane[laneid]对应的SrcL值

    V[d, dstwidth, laneid] = data;
}
```

![shfl.up](../../../figs/isa/inst/shfl.up.png)

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
