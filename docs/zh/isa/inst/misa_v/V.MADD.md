# V.MADD

## 说明

乘加(*Multiply and ADD*)<br>
计算第一个源操作数乘以第二个源操作数，其结果再加上第三个源操作数，将结果写入目的寄存器。

使用本指令应保证源操作数符号性相同，否则不保证计算结果的正确性。

## 汇编语法

```asm
    v.madd SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, SrcD<.reuse>.{T}, ->RegDst.{W}
```

## 汇编符号

- **SrcL**：第一个源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：第二个源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcD**：第三个源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。

## 编码格式

![V.MADD](../../../figs/bitfield/svg/Instruction_64bit/V.MADD.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {c, srctype3} = DecodeINT(SrcD); 
    integer {m, srctype1} = DecodeINT(SrcL);
    integer {n, srctype2} = DecodeINT(SrcR); 
    integer {d, dstwidth} = DecodeDst(RegDst); 

    if (pmask[laneid] == 1) {
        bits(64) operand1 = V[m, srctype1, laneid];
        bits(64) operand2 = V[n, srctype2, laneid];
        bits(64) operand3 = V[c, srctype3, laneid];
        bits(64*2) result = operand3 +(s) operand1 *(s) operand2;

        V[d, dstwidth, laneid] = result[63:0];   // 根据输出寄存器位宽对结果进行截断
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane中默认写0
    }
}
```

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
