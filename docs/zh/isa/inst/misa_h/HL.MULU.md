# HL.MULU

## 说明

无符号乘(*Multiply, Unsigned*)  
无符号计算左源操作数乘以右源操作数，将结果的`低64位`写入第一个目的寄存器，结果的`高64位`写入第二个目的寄存器。

本指令标准版本请见[MULU](../misa_g/MULU.md)。

## 汇编语法

```asm
    hl.mulu SrcL, SrcR, ->Dst0, Dst1
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器，两个目的寄存器分别编码于RegDst0和RegDst1字段。
- **Dst0**：第一个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。
- **Dst1**：第二个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.MULU](../../../figs/bitfield/svg/Instruction_48bit_16/HL.MULU.svg)

- 高32bit编码：

![HL.MULU](../../../figs/bitfield/svg/Instruction_48bit_32/HL.MULU.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d0 = UInt(RegDst0);
    integer d1 = UInt(RegDst1);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);

    bits(64) operand1 = R[m, 64];
    bits(64) operand2 = R[n, 64];
    bits(128) result = operand1 *(u) operand2;

    R[d0, 64] = result[63:0];
    R[d1, 64] = result[127:64];
```

## 汇编索引模式

输入输出可选组合如下：

| 输入组合 | 输出组合 |
|---------|-----------|
| **a1, a2**  | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **a1, t#2** | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **a1, u#2** | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **t#1, a2**  | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **t#1, t#2** | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **t#1, u#2** | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **u#1, a2**  | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **u#1, t#2** | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **u#1, u#2** | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |

## 注意事项

如果两个目的寄存器相同，硬件执行结果不可知。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
