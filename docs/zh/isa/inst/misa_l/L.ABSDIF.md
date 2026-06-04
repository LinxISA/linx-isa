# L.ABSDIF

## 说明

整数绝对差值(*Integer Absolute Difference*)<br>
计算左源寄存器和右源寄存器中整型数据的差值的绝对值，并将结果写入目的寄存器。

## 汇编语法

```asm
    l.absdif SrcL.<T>, SrcR.<T>, ->RegDst.d, sat
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选类型包括sb, sh, sw, sd, ub, uh, uw, ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。
- **sat（saturation）**：支持饱和计算的标志。

## 编码格式

![L.ABSDIF](../../../figs/bitfield/svg/Instruction_64bit/L.ABSDIF.svg)

饱和计算sat位编码：

| sat | 含义 |
|------|-------|
| 0 | 无饱和计算（默认） |
| 1 | 启用饱和计算 |

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, srcWidth1} = DecodeINT(SrcL);
    integer {n, srcWidth2} = DecodeINT(SrcR);
    integer {d, dstWidth} = DecodeDst(RegDst);

    bits(srcWidth1) operand1 = SREG[m, srcWidth1];
    bits(srcWidth2) operand2 = SREG[n, srcWidth2];

    bits(64) diff = operand1 - operand2;
    bits(64) result = (diff < 0) ? -diff : diff;

    if (sat == 1) {
        if (result >= MaxValue) result = MaxValue;
        if (result <= MinValue) result = MinValue;
    }
    SREG[d, dstWidth] = result;
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.ABSDIF](../misa_v/V.ABSDIF.md)。
