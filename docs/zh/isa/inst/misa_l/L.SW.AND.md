# L.SW.AND

## 说明

存储字·相与(*Store Word And*)<br>
本指令执行如下的原子操作：从左源寄存器指向的内存位置原子性地加载 32 位数据，与右源寄存器的低 32 位**按位与**，将结果原地写回内存。

本指令可以选择带有 **Store-Release** 语义。

## 汇编语法

```asm
l.sw.and<.{rl, f, rlf}> [SrcL<.ud>], SrcR.<T>
```

## 汇编符号

- 指令可以带有如下可选后缀：
    - **.rl**：表示带有Store-Release的同步语义。
    - **.f**：表示内存访问发生在远端Cache中。
    - 其他后缀（例如.rlf）为以上基础后缀的组合形式。
- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **.ud**: 左源寄存器后缀，表示其作为 64 位操作数。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：操作数的类型标识，可选类型包括sw,sd,uw,ud。

## 编码格式

![L.SW.AND](../../../figs/bitfield/svg/Instruction_64bit/L.SW.AND.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
integer {m, srcWidth1} = DecodeINT(SrcL);
integer {n, srcWidth2} = DecodeINT(SrcR); 
integer {d, dstWidth} = DecodeDst(RegDst);

Atomic {
    bits(64) address = SREG[m, srcWidth1];
    bits(32) operand = SREG[n, srcWidth2];

    bits(32) oldValue = Mem[address][31:0];
    bits(32) newValue = oldValue & operand;

    Mem[address] = newValue;
}
```

## 注意事项

1. 如果源寄存器位宽不满足本指令的要求，那么硬件不保证执行结果的正确性（执行结果不可知）。
2. 如果任意源寄存器是向量寄存器，那么应使用别名指令[V.SW.AND](../misa_v/V.SW.AND.md)。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.SW.AND](../misa_v/V.SW.AND.md)。
