# L.FABS

## 说明

浮点数绝对值(*Floating-point Absolute Value*)<br>
将源寄存器中的浮点数取其绝对值（即清除符号位，保留尾数和指数部分），并将结果以相同数据格式写入目的寄存器中。

## 汇编语法

```asm
    l.fabs SrcL.<T>, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选类型包括fb, fh, fs, fd等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

## 编码格式

![L.FABS](../../../figs/bitfield/svg/Instruction_64bit/L.FABS.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码源寄存器域：[DecodeFP](../LibPseudoCode.md#locationM)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, srcWidth} = DecodeFP(SrcL);
    integer {d, dstWidth} = DecodeDst(RegDst); 

    bits(srcWidth) operand = SREG[m, 64];
    bits(64) result = |operand|;

    SREG[d, dstWidth] = result;       
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.FABS](../misa_v/V.FABS.md)。
