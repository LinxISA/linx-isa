# L.REV

## 说明

翻转(*Reverse*)<br>
在源操作数的每个 `M` 位范围内以 `N` 位为单位进行高低位翻转，结果写到目的寄存器中。

## 汇编语法

```asm
    l.rev SrcL.<T>, M, N, ->RegDst.d
```

## 汇编符号

- **SrcL**：源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选参数根据寄存器类型不同而有所区别。
- **M**：表示每次进行翻转操作的操作域位宽，合法取值包括：{2, 4, 8, 16, 32, 64}。该参数减1后编码于immr字段。
- **N**：表示每个操作域内进行翻转操作的单位，合法取值包括：{1, 2, 4, 8, 16, 32}。该参数编码于imml字段。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **d**：目的寄存器的位宽标识（d表示64-bit）。

如果源寄存器是向量寄存器，那么目的寄存器最终写入的值由实现定义。

!!! note "注意事项！"

    M和N的取值必须小于源寄存器位宽，否则硬件执行结果不可知。

## 编码格式

![L.REV](../../../figs/bitfield/svg/Instruction_64bit/L.REV.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, srcWidth}  = DecodeINT(SrcL);
    integer {d, dstWidth} = DecodeDst(RegDst); 
    integer M = UInt(immr) + 1;
    integer N = UInt(imml);

    // 以下情况报非法指令
    if M isnot in range{2, 4, 8, 16, 32, 64} then Exception(EC_ILLEGAL);
    if N isnot in range{1, 2, 4, 8, 16, 32}  then Exception(EC_ILLEGAL);
    if M <= N                                then Exception(EC_ILLEGAL);  

    bits(srcWidth) operand = SREG[m, srcWidth];
    bits(dstWidth) result;

    integer fieldnum = 64 / M;
    integer elementnum = M / N;
    integer idx = 0;
    integer ridx;
    for i = 0 to (fieldnum - 1) {
        ridx = idx + (elementnum - 1) * N;
        for j = 0 to (elementnum - 1) {
            result[ridx+(N-1): ridx] = operand[idx+(N-1) : idx];
            idx += N;
            ridx -= N;
        }
    }

    SREG[d, dstWidth] = result;    
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.REV](../misa_v/V.REV.md)。
