# L.LWUI

## 说明

立即数偏移·无符号字加载 (*Load Unsigned Word with Immediate Offset*)<br>
本指令使用 **基址寄存器** 加 **左移两位的有符号立即数偏移** 的结果作为有效地址，从内存中加载四个字节（byte）的数据写入目的寄存器。

## 汇编语法

```asm
    l.lwui<.local> [SrcL<.ud>, simm], ->RegDst.d
```

## 汇编符号

- **local**：表示访问Tile寄存器的空间，缺省表示访问内存空间。
- **SrcL**：基址寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **simm**：有符号立即数偏移，该参数在simm24字段中的编码为simm/4。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

如果源寄存器是向量寄存器，那么目的寄存器最终写入的值由实现定义。

## 编码格式

![L.LWUI](../../../figs/bitfield/svg/Instruction_64bit/L.LWUI.svg)

其中，L标志位含义如下：

| L(local) | 含义 |
|----------|--------|
| 0 | 访问内存空间 |
| 1 | 访问Tile寄存器空间  |

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md#locationF)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md#locationG)

```c
    integer {m, srcWidth} = DecodeINT(SrcL);
    integer {d, dstWidth} = DecodeDst(RegDst); 

    bits(64) base = SREG[m, srcWidth];
    bits(64) offset = SignExtend(simm24);
    bits(64) address = base + (offset << 2);

    bits(32) data = Mem[address][31:0];
    SREG[d, dstWidth] = ZeroExtend(data, 64);
```

## 注意事项

1. 该指令支持地址非对齐访问。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.LWUI](../misa_v/V.LWUI.md)。
