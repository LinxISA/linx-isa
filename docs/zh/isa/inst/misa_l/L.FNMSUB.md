# L.FNMSUB

## 说明

浮点数乘减取负(*Floating-point Multiply-Sub Negative*)<br>
将第一个源寄存器和第二个源寄存器的浮点数相乘，用未舍入的积减去第三个源寄存器的浮点数，将舍入后的结果取负后写入目的寄存器。

## 汇编语法

```asm
    l.fnmsub SrcL.<T>, SrcR.<T>, SrcA<.T>, ->RegDst.d
```

## 汇编符号

- **SrcL**：第一个源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：第二个源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcA**：第三个源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选类型包括fb, fh, fs, fd等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

## 编码格式

![L.FNMSUB](../../../figs/bitfield/svg/Instruction_64bit/L.FNMSUB.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码源寄存器域：[DecodeFP](../LibPseudoCode.md#locationM)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, srcType1} = DecodeFP(SrcL);
    integer {n, srcType2} = DecodeFP(SrcR);
    integer {a, srcType3} = DecodeFP(SrcA); 
    integer {d, dstWidth} = DecodeDst(RegDst); 

    if (srcType1 != srcType2 || srcType1 != srcType3) then undefined;

    srcType1 operand1 = SREG[m, srcWdith1];
    srcType2 operand2 = SREG[n, srcWdith2];
    srcType3 operand3 = SREG[a, srcWdith3];

    bits(64) result = -(operand1 * operand2 - operand3);
    SREG[d, dstWidth] = result;   
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.FNMSUB](../misa_v/V.FNMSUB.md)。
