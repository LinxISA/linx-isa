# C.LDI

## 说明

立即数偏移·双字加载 (*Load Doubleword with Immediate Offset*)  
以 **基址寄存器值** 加 **左移三位后的有符号立即数偏移** 的结果为地址，从内存加载 `八个字节` 的数据后写到T寄存器。

本指令的标准形式请见[LDI](../misa_g/LDI.md)。

## 汇编语法

```asm
    c.ldi [SrcL, simm], ->t
```

## 汇编符号

- **SrcL**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：有符号立即数偏移,是-128到+120范围内的8的倍数，在simm5字段中编码为simm/8。
- **->**：用于指示目的寄存器。
- **t**：目的寄存器，代表块内的T寄存器队列。

## 编码格式

![C.LDI](../../../figs/bitfield/svg/Instruction_16bit/C.LDI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer s = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) baseAddr = R[s, datawidth];
    bits(datawidth) offset = SignExtend(simm5);
    bits(datawidth) address = baseAddr + (offset << 3);
    bits(datawidth) data = Mem[address];
    T[id] = data;
```

## 汇编索引模式

- 指令只能输出到块内t寄存器

```asm
    c.ldi [a1, simm],  ->t           /* 单寄存器绝对索引 */
    c.ldi [t#1, simm], ->t           /* 单寄存器相对索引 */
    c.ldi [u#1, simm], ->t           /* 单寄存器相对索引 */
```

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
