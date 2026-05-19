# SDI

## 说明

立即数偏移·存双字(*Store Doubleword with Immediate Offset*)  
将源数据寄存器中 `八个字节` 存入目标地址指向的内存中，目标地址由 **基址寄存器** 加 **左移三位的有符号立即数偏移** 计算得到。 

## 汇编语法

```c
    sdi SrcL, [SrcR, simm]
```

## 汇编符号

- **SrcL**：数据寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：有符号立即数偏移，是-16384到+16376范围内的8的倍数，在simm12字段中编码为simm/8。

## 编码格式

![SDI](../../../figs/bitfield/svg/Instruction_32bit/SDI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer datawidth = 64;

    bits(datawidth) data = R[m, datawidth];
    bits(datawidth) baseAddr = R[n, datawidth];
    bits(datawidth) offset = SignExtend(simm12);

    bits(datawidth) address = baseAddr + (offset << 3);
    Mem[address] = data[63:0];
```

## 汇编索引模式

```asm
sdi a1, [a2, simm]     /* 双寄存器绝对索引 */
sdi a1, [t#2, simm]    /* 双寄存器混合索引 */
sdi a1, [u#2, simm]    /* 双寄存器混合索引 */
sdi t#1, [a2, simm]    /* 双寄存器混合索引 */
sdi t#1, [t#2, simm]   /* 双寄存器相对索引 */
sdi t#1, [u#2, simm]   /* 双寄存器相对索引 */
sdi u#1, [a2, simm]    /* 双寄存器混合索引 */
sdi u#1, [t#2, simm]   /* 双寄存器相对索引 */
sdi u#1, [u#2, simm]   /* 双寄存器相对索引 */
```

## 注意事项

该指令支持地址非对齐访问。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
