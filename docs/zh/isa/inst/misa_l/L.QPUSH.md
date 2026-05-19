# L.QPUSH

## 说明

入队列(*Push to Queue*)<br>
将 右源操作数 push 到左源操作数指定的GQM队列中(默认push到队尾)，并将执行结果写入到目的寄存器。

## 汇编语法

```asm
    l.qpush SrcL.ud, SrcR.ud, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **ud**：表示操作数为64位整型数据。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。数据编码如下：
    - [9:0] 表示写入后队列中的剩余单元数。
    - [63:62] 0表示写入成功，1表示队列满，2表示数据破坏，3保留。
- **.d**：表示目的寄存器的位宽为64位。

## 编码格式

![L.QPUSH](../../../figs/bitfield/svg/Instruction_64bit/L.QPUSH.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, srcWidth1} = DecodeINT(SrcL);
    integer {n, srcWidth2} = DecodeINT(SrcR); 
    integer {d, dstWidth} = DecodeDst(RegDst); 

    bits(srcWidth1) address = SREG[m, srcWidth1];
    bits(srcWidth2) operand = SREG[n, srcWidth2];
    integer remainNums, state;

    {remainNums, state} = GQM[address].push_back(operand);    // push到队尾

    bit(64) result;                         //执行的结果
    result[9:0] = remainNums;               //表示写入后队列中的剩余单元数。
    result[63:62] = state;                  //0表示写入成功，1表示队列满，2表示数据破坏，3保留。

    SREG[d, dstWidth] = result;
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.QPUSH](../misa_v/V.QPUSH.md)。
