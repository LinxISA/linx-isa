# L.CLZ

## 说明

计数前导零位(*Count Leading Zero bits*)<br>
从源操作数的 `M` 位开始，连续 `N` 位的范围内，从高位至低位计数遇到第一个`1`之前二进制`0`的位数，将计数结果写到目的寄存器中。

因此，如果输入为0，则输出为XLEN，如果输入的最高有效位为1，则输出为0。

## 汇编语法

```asm
    l.clz SrcL.<T>, M, N, ->RegDst.d
```

## 汇编符号

- **SrcL**：源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选参数根据寄存器类型不同而有所区别。
- **M**：计数范围的起始位，取值范围为：[63, 0]。该参数编码于imms字段。
- **N**：计数范围的总位数，取值范围为：[64, 1]。该参数减1后编码于imml字段。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

如果源寄存器是向量寄存器，那么目的寄存器最终写入的值由实现定义。

!!! note "注意事项！"

    M和N的取值必须小于源寄存器位宽，否则硬件执行结果不可知。

## 编码格式

![L.CLZ](../../../figs/bitfield/svg/Instruction_64bit/L.CLZ.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)
- 转换为十进制数：[UInt()](../LibPseudoCode.md)

```c
    integer {m, srcWidth}  = DecodeINT(SrcL);
    integer {d, dstWidth} = DecodeDst(RegDst); 
    integer M = UInt(imms);
    integer N = UInt(imml) + 1;

    bits(srcWidth) operand = SREG[m, srcWidth];
    bits(srcWidth*2) newoperand = (operand << srcWidth) | operand;

    bits(dstWidth) result = 0;
    foreach (i from (N-1) to 0 by 1 in dec) {
        if newoperand[M+i] == 0b0 then result++;
        else break;
    }

    SREG[d, dstWidth] = result;
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.CLZ](../misa_v/V.CLZ.md)。
