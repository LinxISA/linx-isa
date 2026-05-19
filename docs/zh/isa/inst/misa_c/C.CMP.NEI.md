# C.CMP.NEI

## 说明

立即数不相等比较(*Compare with Immediate if Not Equal*)  
比较前序输出至T队列的指令结果和有符号扩展立即数，如果不等则将1写到T寄存器中，否则写入0。

本指令的标准形式请见[CMP.NEI](../misa_g/CMP.NEI.md)。

## 汇编语法

```
    c.cmp.nei t#1, simm, ->t
```

## 汇编符号

- **t#1**：源寄存器，索引前序第一条输出至T队列的指令结果。
- **simm**：5位有符号立即数。
- **->**：用于指示目的寄存器。
- **t**：目的寄存器，代表块内的T寄存器队列。

## 编码格式

![C.CMP.NEI](../../../figs/bitfield/svg/Instruction_16bit/C.CMP.NEI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) operand = TR1[63:0];
    bits(datawidth) simm = SignExtend(simm5);

    bits(datawidth) result = (operand != simm ? 1 : 0);
    T[id] = result;
```

## 汇编索引模式

```asm
    c.cmp.nei t#1, simm, ->t         /* 单寄存器相对索引 */
```

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
