# L.QPOP

## 说明

出队列(*Pop from Queue*)<br>
该指令读出由 左源操作数 指定的GQM队列的数据并输出至目的寄存器。同时如果读出成功，返回**状态0**，如果读出失败，返回**状态1**。

## 汇编语法

```asm
    l.qpop SrcL.ud, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **.ud**: 左源寄存器后缀，表示其作为 64 位操作数。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

## 编码格式

![L.QPOP](../../../figs/bitfield/svg/Instruction_64bit/L.QPOP.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, 64}  = DecodeINT(SrcL);
    integer {d, 64} = DecodeDst(RegDst); 

    integer state;
    bit(64) data;

    bits(64) address = SREG[m, 64];
    {state, data} = GQM[address].pop();

    SREG[d, 64] = data;     // 读出成功
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.QPOP](../misa_v/V.QPOP.md)。
