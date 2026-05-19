# L.MADD

## 说明

乘加(*Multiply and ADD*)<br>
本指令用第一个源操作数乘以第二个源操作数，其结果再加上第三个源操作数，并将结果写入目的寄存器。

应保证源操作数符号性相同，否则不保证计算结果的正确性。

## 汇编语法

```asm
    l.madd SrcL.<T>, SrcR.<T>, SrcD<.T>, ->RegDst.d
```

## 汇编符号

- **SrcL**：第一个源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：第二个源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcD**：第三个源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选参数根据寄存器类型不同而有所区别。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

如果源寄存器是向量寄存器，那么目的寄存器最终写入的值由实现定义。

## 编码格式

![L.MADD](../../../figs/bitfield/svg/Instruction_64bit/L.MADD.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, sign1} = DecodeINT(SrcL);
    integer {n, sign2} = DecodeINT(SrcR); 
    integer {c, sign3} = DecodeINT(SrcD); 
    integer {d, 64} = DecodeDst(RegDst); 

    if sign1 != sign2 then undefined;

    bits(64) operand1 = SREG[m, 64];
    bits(64) operand2 = SREG[n, 64];
    bits(64) operand3 = SREG[c, 64];
    bits(64) result;

    if sign1 == 0 then
        result = operand3 +(u) operand1 *(u) operand2;
    else
        result = operand3 +(s) operand1 *(s) operand2;

    SREG[d, 64] = result;
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.MADD](../misa_v/V.MADD.md)。
