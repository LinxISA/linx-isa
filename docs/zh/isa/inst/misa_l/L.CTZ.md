# L.CTZ

## 说明

计数尾随零位(*Count Trailing Zero bits*)<br>
从源操作数的 `M` 位开始连续 `N` 位的范围内，从低位至高位计数遇到第一个`1`之前二进制`0`的位数，将计数结果写到目的寄存器中。

因此，如果输入为0，则输出为XLEN，如果输入的最低有效位为1，则输出为0。

## 汇编语法

```
    l.ctz SrcL.<T>, M, N, ->RegDst.d
```

## 汇编符号

- **SrcL**：源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选参数根据寄存器类型不同而有所区别。
- **M**：计数范围的起始位，取值范围为：[63, 0]。该参数编码于imms字段。
- **N**：计数范围的总位数，取值范围为：[64, 1]。该参数减1后编码于imml字段。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

!!! note "注意事项！"

    M和N的取值必须小于源寄存器位宽，否则硬件执行结果不可知。

寄存器可选类型见下表：

| 寄存器 | 可选类型 | 可选后缀（T） |
|-------|----------|-------------|
| SrcL | ri0~ri11; t,u; P | sd,ud（可缺省） |
| SrcL | lb0, lb1, lb2    | uh |
| RegDst | t,u | d（可缺省） |

## 编码格式

![L.CTZ](../../../figs/bitfield/svg/Instruction_64bit/L.CTZ.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)
- 转换为十进制数：[UInt()](../LibPseudoCode.md)

```c

    integer {m, 64}  = DecodeINT(SrcL);
    integer {d, 64} = DecodeDst(RegDst); 
    integer M = UInt(imms);
    integer N = UInt(imml) + 1;

    bits(64) operand = SREG[m, 64];
    bits(64*2) newoperand = (operand << 64) | operand;

    bits(64) result = 0;
    foreach (i from 0 to (N-1) by 1 in dec) {
        if newoperand[M+i] == 0 then result++;
        else break;
    }

    SREG[d, 64] = result;
```

<!-- 
## 汇编索引模式

```asm
ctz a1        /* 单寄存器绝对索引 */
ctz t#1       /* 单寄存器相对索引 */
ctz a1,->a2   /* 指令输出到私有寄存器 */
ctz t#1,->a2  /* 指令输出到私有寄存器 */
ctz a1,=>a2   /* 指令输出到全局寄存器 */
ctz t#1,=>a2  /* 指令输出到全局寄存器 */
```
 -->

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.LB](../misa_v/V.LB.md)。
