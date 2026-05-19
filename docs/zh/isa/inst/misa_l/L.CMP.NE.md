# L.CMP.NE

## 说明

不相等比较(*Compare if Not Equal*)<br>
本指令对左源寄存器和右源寄存器中特定类型的操作数进行比较，若**不相等**则将`1`写入目的寄存器，否则写入`0`。

## 汇编语法

```asm
    l.cmp.ne SrcL.<T>, SrcR.<T>, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选参数根据寄存器类型不同而有所区别。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

如果源寄存器是向量寄存器，那么目的寄存器最终写入的值由实现定义。

## 编码格式

![L.CMP.NE](../../../figs/bitfield/svg/Instruction_64bit/L.CMP.NE.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, 64} = DecodeINT(SrcL);
    integer {n, 64} = DecodeINT(SrcR);
    integer {d, 64} = DecodeDst(RegDst); 

    bits(64) operand1 = SREG[m, 64];
    bits(64) operand2 = SREG[n, 64];
    bits(64) result = (operand1 != operand2 ? 1 : 0);
    
    SREG[d, 64] = result;
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.CMP.NE](../misa_v/V.CMP.NE.md)。
