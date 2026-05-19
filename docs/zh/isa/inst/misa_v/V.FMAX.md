# V.FMAX

## 说明

浮点数最大值(*Floating-point Maximum*)<br>
比较左源寄存器和右源寄存器中的浮点数，将**较大值**写入目的寄存器中。

## 汇编语法

```asm
    v.fmax SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, ->RegDst.{W}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括fb, fh, fs, fd等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。

## 编码格式

![V.FMAX](../../../figs/bitfield/svg/Instruction_64bit/V.FMAX.svg)

## 执行方式

- 解码源寄存器域：[DecodeFP](../LibPseudoCode.md#locationM)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {m, srctype1} = DecodeFP(SrcL);
    integer {n, srctype2} = DecodeFP(SrcR); 
    integer {d, dstwidth} = DecodeDst(RegDst); 

    if srctype1 != srctype2 then undefined;

    if (pmask[laneid] == 1) {
        srctype1 operand1 = V[m, srctype1, laneid];
        srctype2 operand2 = V[n, srctype2, laneid];

        bits(64) result = (operand1 > operand2 ? operand1 : operand2);
        
        V[d, dstwidth, laneid] = result;  // 根据输出寄存器位宽对结果进行截断
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane中默认写0
    }
}
```

!!! note "注意！"

    值-0.0被视为小于值+0.0。  
    如果两个输入都是NaN，则结果是规范NaN。  
    如果只有一个操作数是NaN，则结果是非NaN操作数。

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
