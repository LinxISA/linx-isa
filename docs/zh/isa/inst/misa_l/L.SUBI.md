# L.SUBI

## 说明

减立即数(*Substract Immediate*)<br>
本指令对源寄存器中指定类型的操作数与无符号立即数 **相减**，并将结果写入目的寄存器。

## 汇编语法

```asm
    l.subi SrcL.<T>, uimm, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选参数根据寄存器类型不同而有所区别。
- **uimm**：12位无符号立即数，编码于uimm12域。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

## 编码格式

![L.SUBI](../../../figs/bitfield/svg/Instruction_64bit/L.SUBI.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md#locationG)

```c
    integer {m, 64}  = DecodeINT(SrcL);
    integer {d, 64} = DecodeDst(RegDst); 

    bits(64) operand = SREG[m, 64];
    bits(64) uimm = ZeroExtend(uimm12);
    bits(64) result = operand - uimm;

    SREG[d, 64] = result;
```

## 注意事项

1. 结果忽略算数溢出。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.SUBI](../misa_v/V.SUBI.md)。
