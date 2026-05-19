# C.SWI

## 说明

立即数偏移·存双字(*Store Doubleword with Immediate Offset*)  
将源数据寄存器中低位 `四个字节` 存入目标地址指向的内存中，目标地址由 **基址寄存器值** 加 **左移两位的有符号立即数偏移** 计算得到。

本指令的标准形式请见[SWI](../misa_g/SWI.md)。

## 汇编语法

```c
    c.swi t#1, [SrcL, simm]
```

## 汇编符号

- **t#1**：数据寄存器，索引前序第一条输出至T寄存器的指令结果。
- **SrcL**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：有符号立即数偏移,是-64到+60范围内的4的倍数，在simm5字段中编码为simm/4。

## 编码格式

![C.SWI](../../../figs/bitfield/svg/Instruction_16bit/C.SWI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) data = TR1[63:0];
    bits(datawidth) baseAddr = R[m, datawidth];
    bits(datawidth) offset = SignExtend(simm5);

    bits(datawidth) address = baseAddr + (offset << 2);
    Mem[address] = data[31:0];
```

## 汇编索引模式

```asm
    c.swi t#1, [a2, simm]          /* 双寄存器绝对索引 */
    c.swi t#1, [t#2, simm]         /* 双寄存器相对索引 */
    c.swi t#1, [u#2, simm]         /* 双寄存器相对索引 */
```

!!! note "注意! "

    1. 本指令不占私有寄存器槽位。

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
