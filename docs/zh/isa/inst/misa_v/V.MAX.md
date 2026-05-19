# V.MAX

## 说明

最大值(*Maximum*)<br>
比较左源寄存器和右源寄存器中的整型数据，将**较大值**写入目的寄存器。

## 汇编语法

```asm
    v.max SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, ->RegDst.{W}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指令操作数的浮点类型标识，包括sb,sh,sw,sd,ub,uh,uw,ud。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。

## 编码格式

![V.MAX](../../../figs/bitfield/svg/Instruction_64bit/V.MAX.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {m, srctype1} = DecodeINT(SrcL);
    integer {n, srctype2} = DecodeINT(SrcR); 
    integer {d, dstwidth} = DecodeDst(RegDst);

    if (pmask[laneid] == 1) {
        bits(64) operand1 = V[m, srctype1, laneid];
        bits(64) operand2 = V[n, srctype2, laneid];
        bits(64) result = (operand1 > operand2 ? operand1 : operand2);
    
        V[d, dstwidth, laneid] = result;  // 根据输出寄存器位宽对结果进行截断
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane中默认写0
    }
}
```

<!-- ## 汇编索引模式

```asm
max.h a1, a2           /* 双寄存器绝对索引 */
max.h t#1, a2          /* 双寄存器相对绝对索引 */
max.h a1, t#2          /* 双寄存器相对绝对索引 */
max.h t#1, t#2         /* 双寄存器相对索引 */
max.s a1, a2           /* 单精度浮点操作数，可使用.d,.s,.h */
max.s t#1, a2          /* 单精度浮点操作数，可使用.d,.s,.h */
max.s a1, t#2          /* 单精度浮点操作数，可使用.d,.s,.h */
max.s t#1, t#2         /* 单精度浮点操作数，可使用.d,.s,.h */
max.s a1, a2,->a1      /* 指令输出到私有寄存器 */
max.s t#1, a2,->a1     /* 指令输出到私有寄存器 */
max.s a1, t#2,->a1     /* 指令输出到私有寄存器 */
max.s t#1, t#2,->a1    /* 指令输出到私有寄存器 */
max.d a1, a2,=>a1      /* 指令输出到全局寄存器 */
max.d t#1, a2,=>a1     /* 指令输出到全局寄存器 */
max.d a1, t#2,=>a1     /* 指令输出到全局寄存器 */
max.d t#1, t#2,=>a1    /* 指令输出到全局寄存器 */
``` -->

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
