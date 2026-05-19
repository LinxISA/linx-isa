# HL.MADDW

## 说明

字·乘加(*Multiply and Add Word*)  
有符号计算第一个源操作数乘以第二个源操作数，再加上第三个源操作数，将结果的`低32位`有符号扩展后写入第一个目的寄存器，结果的`高32位`有符号扩展后写入第二个目的寄存器。

## 汇编语法

```asm
    hl.maddw SrcL, SrcR, SrcD, ->Dst0, Dst1
```

## 汇编符号

- **SrcL**：第一个源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：第二个源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcD**：第三个源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器，两个目的寄存器分别编码于RegDst0和RegDst1字段。
- **Dst0**：第一个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。
- **Dst1**：第二个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.MADDW](../../../figs/bitfield/svg/Instruction_48bit_16/HL.MADDW.svg)

- 高32bit编码：

![HL.MADDW](../../../figs/bitfield/svg/Instruction_48bit_32/HL.MADDW.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d0 = UInt(RegDst0);
    integer d1 = UInt(RegDst1);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer k = UInt(SrcD);

    bits(32) operand1 = R[m, 32];
    bits(32) operand2 = R[n, 32];
    bits(32) operand3 = R[k, 32];
    bits(64) result = operand1 *(s) operand2 +(s) operand3;

    R[d0, 64] = SignExtend(result[31:0]);
    R[d1, 64] = SignExtend(result[63:32]);
```

## 汇编索引模式

| 输入<br>组合 | 输出<br>组合1 | 输出<br>组合2 | 输出<br>组合3 | 输出<br>组合4 | 输出<br>组合5 | 输出<br>组合6 | 输出<br>组合7 | 输出<br>组合8 | 输出<br>组合9 |
|-------------|---------------|--------------|--------------|--------------|---------------|--------------|--------------|---------------|--------------|
| a1,  a2,  a3  | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| a1,  t#2, a3  | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| a1,  u#2, a3  | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| t#1, a2,  a3  | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| t#1, t#2, a3  | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| t#1, u#2, a3  | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| u#1, a2,  a3  | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| u#1, t#2, a3  | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| u#1, u#2, a3  | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| a1,  a2,  t#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| a1,  t#2, t#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| a1,  u#2, t#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| t#1, a2,  t#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| t#1, t#2, t#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| t#1, u#2, t#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| u#1, a2,  t#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| u#1, t#2, t#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| u#1, u#2, t#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| a1,  a2,  u#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| a1,  t#2, u#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| a1,  u#2, u#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| t#1, a2,  u#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| t#1, t#2, u#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| t#1, u#2, u#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| u#1, a2,  u#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| u#1, t#2, u#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |
| u#1, u#2, u#3 | t, t | t, u | t, a4 | u, t | u, u | u, a4 | a4, t | a4, u | a4, a5 |


## 备注

本指令属于[扩展指令集](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
