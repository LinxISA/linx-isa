# L.FRECIP

## 说明

浮点数倒数(*Floating-point Reciprocal Value*)<br>
计算源寄存器中浮点数的倒数（即执行算术运算 1.0 / operand），并将结果以相同浮点格式（如单精度或双精度）写入目的寄存器中。

## 汇编语法

```asm
    l.frecip SrcL.<T>, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选类型包括fb, fh, fs, fd等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

## 编码格式

![L.FRECIP](../../../figs/bitfield/svg/Instruction_64bit/L.FRECIP.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码源寄存器域：[DecodeFP](../LibPseudoCode.md#locationM)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, srcWidth} = DecodeFP(SrcL);
    integer {d, dstWidth} = DecodeDst(RegDst); 

    bits(srcWidth) operand = SREG[m, srcWidth];
    bits(64) result = 1.0 / operand;
    
    SREG[d, dstWidth] = result;    
```

!!! note "注意"

    当源操作数为0时，该指令会触发除零例外(DZ)。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.FRECIP](../misa_v/V.FRECIP.md)。
