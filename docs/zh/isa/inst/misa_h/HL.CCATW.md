# CCATWW

拼接·字(*Concatenate Word*)  
左源操作数 `低32位` 左移32位后与右源操作数 `低32位` 相加，然后循环左移 `shamt` 位后将结果的`高32位`符号扩展后写到第一个目的寄存器，`低32位`符号扩展后写到第二个目的寄存器。

## 汇编语法

```asm
    ccatw SrcL, SrcR, shamt, ->Dst0, Dst1
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **shamt**：对操作数左移位数，范围[0, 63]。
- **->**：用于指示目的寄存器。
- **Dst0**：第一个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。
- **Dst1**：第二个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.CCATW](../../../figs/bitfield/svg/Instruction_48bit_16/HL.CCATW.svg)

- 高32bit编码：

![HL.CCATW](../../../figs/bitfield/svg/Instruction_48bit_32/HL.CCATW.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d0 = UInt(RegDst0);
    integer d1 = UInt(RegDst1);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer shrt = 64 - shamt;

    bits(32) operand1 = R[m, 32];
    bits(32) operand2 = R[n, 32];

    bits(64) data = (operand1 << 32) | operand2;
    bits(64) result = (data << shamt) | (data >>(u) shrt);

    R[d0, 64] = SignExtend(result[63:32], 64);
    R[d1, 64] = SignExtend(result[31:0], 64);
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

- 如果两个目的寄存器相同，那么执行结果不可知（硬件决定保留哪个结果）。
- 本指令允许只有一个目的寄存器，此时输出为第一个目的寄存器的结果。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，且**仅允许在标量块内使用**。
