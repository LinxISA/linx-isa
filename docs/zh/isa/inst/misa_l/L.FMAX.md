# L.FMAX

## 说明

浮点数最大值(*Floating-point Maximum*)<br>
比较左源寄存器和右源寄存器中的浮点数，将**较大值**写入目的寄存器中。

## 汇编语法

```asm
    l.fmax SrcL.<T>, SrcR.<T>, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选类型包括fb, fh, fs, fd等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

## 编码格式

![L.FMAX](../../../figs/bitfield/svg/Instruction_64bit/L.FMAX.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码源寄存器域：[DecodeFP](../LibPseudoCode.md#locationM)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, srcType1} = DecodeFP(SrcL);
    integer {n, srcType2} = DecodeFP(SrcR); 
    integer {d, dstWidth} = DecodeDst(RegDst); 

    if srcType1 != srcType2 then undefined;

    srcType1 operand1 = SREG[m, srcWidth1];
    srcType2 operand2 = SREG[n, srcWidth2];

    bits(64) result = (operand1 > operand2 ? operand1 : operand2);
    SREG[d, 64] = result;
```

!!! note "注意！"

    值-0.0被视为小于值+0.0。  
    如果两个输入都是NaN，则结果是规范NaN。  
    如果只有一个操作数是NaN，则结果是非NaN操作数。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.FMAX](../misa_v/V.FMAX.md)。
