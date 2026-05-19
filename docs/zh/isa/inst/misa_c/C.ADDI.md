# C.ADDI

## 说明

加立即数(*ADD Immediate*)  
寄存器值与有符号立即数相加，结果写到目的T寄存器。

本指令的标准形式请见[ADDI](../misa_g/ADDI.md)。

## 汇编语法

```asm
    c.addi SrcL, simm, ->t
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：5位有符号立即数，编码于simm5域。
- **->**：用于指示目的寄存器。
- **t**：目的寄存器，代表块内的T寄存器队列。

## 编码格式

![c.addi](../../../figs/bitfield/svg/Instruction_16bit/C.ADDI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer s = UInt(SrcL);
    integer DataWidth = 64;

    bits(DataWidth) operand = R[s, DataWidth];
    bits(DataWidth) simm = SignExtend(simm5);
    bits(DataWidth) result = operand + simm;
    T[id] = result;
```

## 汇编索引模式

```asm
    c.addi a1, simm,  ->t             /* 单寄存器绝对索引 */
    c.addi t#1, simm, ->t             /* 单寄存器相对索引 */
```

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
