# V.FNES

## 说明

浮点数不相等比较(*Floating-point Not Equal*)<br>
若左源寄存器和右源寄存器的浮点数不相等，则将`1`写入目的寄存器，否则写入`0`。

如果目的寄存器是P寄存器，本指令是一条向量指令，每个lane写P寄存器中对应的1bit。

## 汇编语法

```asm
    v.fnes SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, ->RegDst.{W}
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

![V.FNES](../../../figs/bitfield/svg/Instruction_64bit/V.FNES.svg)

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

        bits(64) result = (operand1 != operand2 ? 1 : 0);
        
        V[d, dstwidth, laneid] = result;    // 根据输出寄存器位宽对结果进行截断
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane中默认写0
    }
}
```

<!-- ## 汇编索引模式

```asm
fne.h a1, a2           /* 双寄存器绝对索引 */
fne.h t#1, a2          /* 双寄存器相对绝对索引 */
fne.h a1, t#2          /* 双寄存器相对绝对索引 */
fne.h t#1, t#2         /* 双寄存器相对索引 */
fne.s a1, a2           /* 单精度浮点操作数，可使用.d,.s,.h */
fne.s t#1, a2          /* 单精度浮点操作数，可使用.d,.s,.h */
fne.s a1, t#2          /* 单精度浮点操作数，可使用.d,.s,.h */
fne.s t#1, t#2         /* 单精度浮点操作数，可使用.d,.s,.h */
fne.s a1, a2,->a1      /* 指令输出到私有寄存器 */
fne.s t#1, a2,->a1     /* 指令输出到私有寄存器 */
fne.s a1, t#2,->a1     /* 指令输出到私有寄存器 */
fne.s t#1, t#2,->a1    /* 指令输出到私有寄存器 */
fne.d a1, a2,=>a1      /* 指令输出到全局寄存器 */
fne.d t#1, a2,=>a1     /* 指令输出到全局寄存器 */
fne.d a1, t#2,=>a1     /* 指令输出到全局寄存器 */
fne.d t#1, t#2,=>a1    /* 指令输出到全局寄存器 */
``` -->

!!! note "注意！"
    
    如果任意操作数是NaN（包括SNaN或QNaN），则该指令输出为0。

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
