# C.OR

## 说明

或(*OR*)  
左源寄存器与右源寄存器按位或，结果写到T寄存器队列。

本指令的标准形式请见[OR](../misa_g/OR.md)。

## 汇编语法

```asm
    c.or SrcL, SrcR, ->t
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器。
- **t**：目的寄存器，代表块内的T寄存器队列。

## 编码格式

![C.OR](../../../figs/bitfield/svg/Instruction_16bit/C.OR.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer DataWidth = 64;

    bits(DataWidth) operand1 = R[m, DataWidth];
    bits(DataWidth) operand2 = R[n, DataWidth];
    bits(DataWidth) result = operand1 | operand2;
    T[id] = result;
```

## 汇编索引模式

- 指令只能输出到块内t寄存器

```asm
    c.or a1, a2,   ->t             /* 双寄存器绝对索引 */
    c.or a1, t#2,  ->t             /* 双寄存器混合索引 */
    c.or a1, u#2,  ->t             /* 双寄存器混合索引 */
    c.or t#1, a2,  ->t             /* 双寄存器混合索引 */
    c.or t#1, t#2, ->t             /* 双寄存器相对索引 */
    c.or t#1, u#2, ->t             /* 双寄存器相对索引 */
    c.or u#1, a2,  ->t             /* 双寄存器混合索引 */
    c.or u#1, t#2, ->t             /* 双寄存器相对索引 */
    c.or u#1, u#2, ->t             /* 双寄存器相对索引 */
```

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
