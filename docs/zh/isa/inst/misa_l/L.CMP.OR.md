# L.CMP.OR

## 说明

或比较(*Compare by Or*)<br>
对左源寄存器中指定数据类型的操作数和右源寄存器中指定数据类型的操作数执行按位或运算，若结果为`非0`则将`1`写入目的寄存器，否则写入`0`。

## 汇编语法

```
    l.cmp.or SrcL.<T>, SrcR.<T>, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选参数根据寄存器类型不同而有所区别。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

寄存器可选类型见下表：

| 寄存器 | 可选类型 | 可选后缀（T） |
|-------|----------|-------------|
| SrcL/SrcR | ri0~ri11; t,u; P | sd,ud（可缺省） |
| SrcL/SrcR | lb0, lb1, lb2    | uh |
| RegDst | t,u | d（可缺省） |

## 编码格式

![L.CMP.OR](../../../figs/bitfield/svg/Instruction_64bit/L.CMP.OR.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, 64, sign1} = DecodeINT(SrcL);
    integer {n, 64, sign2} = DecodeINT(SrcR); 
    integer {d, 64} = DecodeDst(RegDst); 
    bits(64) operand1, operand2;

    if sign1 == 0 then
        operand1 = ZeroExtend(SREG[m, 64]);
    else
        operand1 = SignExtend(SREG[m, 64]);

    if sign2 == 0 then
        operand2 = ZeroExtend(SREG[n, 64]);
    else
        operand2 = SignExtend(SREG[n, 64]);

    bits(64) result = ((operand1 | operand2) != 0 ? 1 : 0);
    
    SREG[d, 64] = result;
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.LB](../misa_v/V.LB.md)。
