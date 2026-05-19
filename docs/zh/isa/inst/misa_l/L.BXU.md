# L.BXU

## 说明

无符号位提取(*Bit eXtract Unsigned*)<br>
从源操作数的第 `M` 位开始连续截取 `N` 位，无符号扩展后写入目的寄存器中。

## 汇编语法

```asm
    l.bxu SrcL.<T>, M, N, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选参数根据寄存器类型不同而有所区别。
- **M**：开始截取的比特位，取值范围为：[63, 0]。该参数编码于imms字段。
- **N**：连续截取的比特位数，取值范围为：[64, 1]。该参数减1后编码于imml字段。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

如果源寄存器是向量寄存器，那么目的寄存器最终写入的值由实现定义。

!!! note "注意事项！"

    M和N的取值必须小于源寄存器位宽，否则硬件执行结果不可知。

## 编码格式

![L.BXU](../../../figs/bitfield/svg/Instruction_64bit/L.BXU.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)
- 转换为十进制数：[UInt()](../LibPseudoCode.md#locationA)

```c
    integer {m, srcWidth} = DecodeINT(SrcL);
    integer {d, dstWidth} = DecodeDst(RegDst); 
    integer M = UInt(imms);
    integer N = UInt(imml) + 1;
    
    bits(srcWidth) operand = SREG[m, srcWidth];
    bits(srcWidth*2) newoperand = (operand << srcWidth) | operand;

    bits(dstWidth) result = ZeroExtend(newoperand[M+N-1:M], N);

    SREG[d, dstWidth] = result;
```

- 当 **M+N <= 64** 时：

![bxu1](../../../figs/isa/inst/bxu1.png){ width="800" }

- 当 **M+N > 64** 且 **N < 64** 时：

![bxu2](../../../figs/isa/inst/bxu2.png){ width="500" }

- 当 **M+N > 64** 且 **N == 64** 时：

![bxu3](../../../figs/isa/inst/bxu3.png){ width="500" }

## 汇编举例

由上面 **M > 0** 且 **N == 64** 时的实现可以看到，该指令对操作数实现了循环移位。

l.bxu指令实现循环移位的方式如下：

- **实现循环左移rol**
```asm
l.bxu t#1.ud, M, 64, ->t.d    /* M = 64 - shamt */
```
此时需将 M 设置为XLEN(即64)减去循环左移的位数后的值。

- **实现循环右移ror**
```asm
l.bxu t#1.ud, M, 64, ->t.d    /* M = shamt */
```
此时需将 M 设置为循环右移的位数。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.BXU](../misa_v/V.BXU.md)。
