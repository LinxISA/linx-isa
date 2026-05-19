# V.MOV

## 说明

寄存器移动(*Move*)<br>
将源寄存器的数据完整拷贝出来，结果写入目的寄存器中。

## 汇编语法

```asm
    v.mov SrcL<.reuse>.{T}, ->RegDst.{W}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指令操作数的浮点类型标识，包括sb,sh,sw,sd,ub,uh,uw,ud。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。

## 编码格式

![V.MOV](../../../figs/bitfield/svg/Instruction_64bit/V.MOV.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {m, srctype1} = DecodeINT(SrcL);
    integer {d, dstwidth} = DecodeDst(RegDst); 

    bits(64) operand = V[m, srctype1, laneid];
    
    V[d, dstwidth, laneid] = operand;  // 根据输出寄存器位宽对结果进行截断
}
```

## 注意事项

**V.MOV是一条不受全局P-Mask控制的指令**，实现对输入寄存器SrcL的全拷贝。

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
