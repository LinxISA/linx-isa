# L.CMP.ANDI

## 说明

立即数相与·比较(*Compare by And Immediate*)<br>
本指令对源寄存器中指定类型的操作数和有符号立即数执行 **按位与** 运算，若结果为`非0`则将`1`写入目的寄存器，否则写入`0`。

## 汇编语法

```asm
    l.cmp.andi SrcL.<T>, simm, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选参数根据寄存器类型不同而有所区别。
- **simm**：12位有符号立即数，编码于simm12字段。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

## 编码格式

![L.CMP.ANDI](../../../figs/bitfield/svg/Instruction_64bit/L.CMP.ANDI.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md#locationF)

```c
    integer {m, 64, sign} = DecodeINT(SrcL);
    integer {d, 64} = DecodeDst(RegDst); 
    bits(64) operand = SREG[m, 64];

    bits(64) simm = SignExtend(simm12);
    bits(64) result = ((operand & simm) != 0 ? 1 : 0);

    SREG[d, 64] = result;
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.CMP.ANDI](../misa_v/V.CMP.ANDI.md)。
