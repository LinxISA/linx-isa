# L.SD.U

## 说明

寄存器偏移无缩放·存双字(*Store Doubleword with Unscaled Register Offset*)<br>
本指令将数据寄存器中八个字节（byte）数据存入目标地址指向的内存，目标地址由 **基址寄存器** 加 **左移shamt位的偏移寄存器** 计算得到。

## 汇编语法

```asm
    l.sd.u<.local> SrcD.<T1>, [SrcL<.ud>, SrcR.<T2><<<shamt>]
```

## 汇编符号

- **local**：表示访问Tile寄存器的空间，缺省表示访问内存空间。
- **SrcD**：数据寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcL**：基址寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：偏移寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T1**：指定操作数的数据类型，可选类型包括sd,ud等。
- **T2**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **shamt**：表示偏移寄存器逻辑左移位数，范围[0, 31]。左移0位默认缺省。

如果输入寄存器是向量寄存器，那么应使用本指令对应的向量版本。

## 编码格式

![L.SD.U](../../../figs/bitfield/svg/Instruction_64bit/L.SD.U.svg)

其中，L标志位含义如下：

| L(local) | 含义 |
|----------|--------|
| 0 | 访问内存空间 |
| 1 | 访问Tile寄存器空间  |

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, srcWidth1, sign1} = DecodeINT(SrcL);
    integer {n, srcWidth2, sign2} = DecodeINT(SrcR);  
    integer {c, srcWidth3, sign3} = DecodeINT(SrcD); 

    bits(64) base = SREG[m, srcWidth1];
    bits(64) offset;

    if (sign2 == 0)
        offset = ZeroExtend(SREG[n, srcWidth2], 64);
    else
        offset = SignExtend(SREG[n, srcWidth2], 64);

    bits(srcWidth3) data = SREG[c, srcWidth3];
    bits(64) address = base + (offset << shamt);

    Mem[address] = data[63:0];
```

## 注意事项

1. 本指令不占块内私有寄存器槽位。
2. 该指令支持地址非对齐访问。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.SD.U](../misa_v/V.SD.U.md)。
