# L.OR

## 说明

取或(*OR*)<br>
该指令对两个源操作数执行 **按位或（OR）** 运算，并将结果写入目的寄存器。操作数支持特定数据类型，支持在运算前对右源操作数进行可选的 **按位取反** 和 **左移shamt位** 操作。

## 汇编语法

```asm
    l.or SrcL.<T>, SrcR.<T><.not><<<shamt>, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。SrcR可以有如下的可选后缀：
    - **.not**：对右源操作数执行逻辑非操作（即每一位取反）。
    - **shamt**：表示右源操作数逻辑左移位数，范围[0, 31]。左移0位默认缺省。
- **T**：指定操作数的数据类型，可选参数根据寄存器类型不同而有所区别。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

如果源寄存器是向量寄存器，那么目的寄存器最终写入的值由实现定义。

## 编码格式

![L.OR](../../../figs/bitfield/svg/Instruction_64bit/L.OR.svg)

其中，SrcRType域编码如下：

|  SrcRType  |  汇编标识  |  解释                       |
|-----------|-----------|-----------------------------|
|  00  |  无  |  无格式转换   |
|  01  |  无  |  保留（reserve）  |
|  10  |  无  |  保留（reserve）  |
|  11  | .not |  not，对操作数按位取反  |

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)
- 转换为十进制数：[UInt()](../LibPseudoCode.md#locationA)
- 对操作数位取反：[Not()](../LibPseudoCode.md)

```c
    integer {m, 64} = DecodeINT(SrcL);
    integer {n, 64} = DecodeINT(SrcR); 
    integer {d, 64} = DecodeDst(RegDst); 
    integer shift_amount = UInt(shamt);

    bits(64) operand1 = SREG[m, 64];
    bits(64) operand2 = SREG[n, 64];

    if SrcRType == 3 then
        operand2 = Not(operand2);

    bits(64) result = operand1 | (operand2 << shift_amount);
    SREG[d, 64] = result;
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.OR](../misa_v/V.OR.md)。
