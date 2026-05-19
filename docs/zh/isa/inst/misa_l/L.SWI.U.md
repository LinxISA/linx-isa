# L.SWI.U

## 说明

立即数偏移无缩放·存字(*Store Word with Unscaled Immediate Offset*)<br>
本指令将数据寄存器中低位四个字节（byte）数据存入目标地址指向的内存中，目标地址由 **基址寄存器** 加 **有符号立即数偏移** 计算得到。

## 汇编语法

```asm
    l.swi.u<.local> SrcL.<T>, [SrcR<.ud>, simm]
```

## 汇编符号

- **local**：表示访问Tile寄存器的空间，缺省表示访问内存空间。
- **SrcL**：数据寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：基址寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指令操作数的数据类型，可选类型包括sw,sd,uw,ud。
- **simm**：有符号立即数偏移，该参数编码于simm24字段。

如果输入寄存器是向量寄存器，那么应使用本指令对应的向量版本。

## 编码格式

![L.SWI.U](../../../figs/bitfield/svg/Instruction_64bit/L.SWI.U.svg)

其中，L标志位含义如下：

| L(local) | 含义 |
|----------|--------|
| 0 | 访问内存空间 |
| 1 | 访问Tile寄存器空间  |

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md#locationF)

```c
    integer {m, srcWidth1} = DecodeINT(SrcL);
    integer {n, srcWidth2} = DecodeINT(SrcR);

    bits(srcWidth1) data = SREG[m, srcWidth1];
    bits(64) base = SREG[n, srcWidth2];
    bits(64) offset = SignExtend(simm24);
    bits(64) address = base + offset;

    Mem[address] = data[31:0];
```

## 注意事项

1. 本指令支持地址非对齐访问。
2. 本指令不占块内私有寄存器槽位。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.SWI.U](../misa_v/V.SWI.U.md)。
