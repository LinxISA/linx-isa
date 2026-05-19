# HL.DIVUW

## 说明

无符号字除法(*Divide Word, Unsigned*)  
无符号计算左源操作数`低32位`除以右源操作数`低32位`，向零舍入，`商数` 符号扩展后写入第一个目的寄存器，`余数`符号扩展后写入第二个目的寄存器中。

## 汇编语法

```asm
    hl.divuw SrcL, SrcR, ->Dst0, Dst1
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器。
- **Dst0**：第一个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。
- **Dst1**：第二个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.DIVUW](../../../figs/bitfield/svg/Instruction_48bit_16/HL.DIVUW.svg)

- 高32bit编码：

![HL.DIVUW](../../../figs/bitfield/svg/Instruction_48bit_32/HL.DIVUW.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d0 = UInt(RegDst0);
    integer d1 = UInt(RegDst1);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);

    bits(32) operand1 = R[m, 64];
    bits(32) operand2 = R[n, 64];
    bits(32) quotient, remainder;

    if operand2 != 0 then
        quotient = operand1 /(u) operand2;
        remainder = operand1 %(u) operand2;
    else
        quotient = 2^32 - 1;
        remainder = operand1;

    R[d0, 64] = SignExtend(quotient[31:0]);
    R[d1, 64] = SignExtend(remainder[31:0]);
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

- 如果出现除以零的情况，商置为 "2^32-1"，有符号扩展到64bit，余数使用被除数的值。
- 如果两个目的寄存器相同，那么执行结果不可知（硬件决定保留哪个结果）。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
