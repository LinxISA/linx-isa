# C.SETC.EQ

## 说明

相等时置位提交(*Set Commit Argument if Equal*)  
当左源操作数等于右源操作数，在本块指令提交时，跳转到指定BPC。

本指令的标准形式请见[SETC.EQ](../misa_g/SETC.EQ.md)

## 汇编语法

```asm
    c.setc.eq SrcL, SrcR
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![C.SETC.EQ](../../../figs/bitfield/svg/Instruction_16bit/C.SETC.EQ.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer DataWidth = 64;

    bits(DataWidth) operand1 = R[m, DataWidth];
    bits(DataWidth) operand2 = R[n, DataWidth];

    BARG.TAKEN = (operand1 == operand2 ? 1 : 0);
```

## 汇编索引模式

```asm
    c.setc.eq  a1, a2               /*双寄存器绝对索引*/
    c.setc.eq  a1, t#2              /*双寄存器绝对索引*/
    c.setc.eq  a1, u#2              /*双寄存器绝对索引*/
    c.setc.eq  t#1, a2              /*双寄存器绝对索引*/
    c.setc.eq  t#1, t#2             /*双寄存器绝对索引*/
    c.setc.eq  t#1, u#2             /*双寄存器绝对索引*/
    c.setc.eq  u#1, a2              /*双寄存器绝对索引*/
    c.setc.eq  u#1, t#2             /*双寄存器绝对索引*/
    c.setc.eq  u#1, u#2             /*双寄存器绝对索引*/
```

!!! note "注意！"

    1. 本指令不占私有寄存器槽位。
    2. 本指令在一个块内只能执行一次。

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
