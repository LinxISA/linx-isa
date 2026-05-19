# C.SUB

## 说明

减法(*Subtract*)  
左源寄存器减右源寄存器，结果写到目的T寄存器。

本指令的标准形式请见[SUB](../misa_g/SUB.md)。

## 汇编语法

```asm
    c.sub SrcL, SrcR, ->t
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器。
- **t**：目的寄存器，代表块内的T寄存器队列。

## 编码格式

![c.sub](../../../figs/bitfield/svg/Instruction_16bit/C.SUB.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer DataWidth = 64;

    bits(DataWidth) operand1 = R[m, DataWidth];
    bits(DataWidth) operand2 = R[n, DataWidth];
    bits(DataWidth) result = operand1 - operand2;
    T[id] = result;
```

## 汇编索引模式

- 指令只能输出到块内t寄存器

```asm
    c.sub a1, a2,   ->t             /* 双寄存器绝对索引 */
    c.sub a1, t#2,  ->t             /* 双寄存器混合索引 */
    c.sub a1, u#2,  ->t             /* 双寄存器混合索引 */
    c.sub t#1, a2,  ->t             /* 双寄存器混合索引 */
    c.sub t#1, t#2, ->t             /* 双寄存器相对索引 */
    c.sub t#1, u#2, ->t             /* 双寄存器相对索引 */
    c.sub u#1, a2,  ->t             /* 双寄存器混合索引 */
    c.sub u#1, t#2, ->t             /* 双寄存器相对索引 */
    c.sub u#1, u#2, ->t             /* 双寄存器相对索引 */
```

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
