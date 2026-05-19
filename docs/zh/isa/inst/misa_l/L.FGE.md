# L.FGE

## 说明

浮点数大于等于比较(*Floating-point Greater Than or Equal*)<br>
若左源寄存器的浮点数大于等于右源寄存器的浮点数，则将`1`写入目的寄存器，否则写入`0`。

## 汇编语法

```asm
    l.fge SrcL.<T>, SrcR.<T>, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选类型包括fb, fh, fs, fd等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

## 编码格式

![L.FGE](../../../figs/bitfield/svg/Instruction_64bit/L.FGE.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码源寄存器域：[DecodeFP](../LibPseudoCode.md#locationM)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, srcType1} = DecodeFP(SrcL);
    integer {n, srcType2} = DecodeFP(SrcR); 
    integer {d, dstWidth} = DecodeDst(RegDst); 

    if srcType1 != srcType2 then undefined;

    srcType1 operand1 = SREG[m, srcWidth1];
    srcType2 operand2 = SREG[n, srcWidth2];

    bits(64) result = (operand1 >= operand2 ? 1 : 0);
    SREG[d, dstWidth] = result;   
```

!!! note "注意！"
    
    如果任意操作数是SNaN，该指令则触发无效操作异常。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.FGE](../misa_v/V.FGE.md)。
