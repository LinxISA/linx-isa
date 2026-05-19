# HL.SDI

## 说明

立即数偏移.存储双字(*Store Doubleword with Immediate offset*)  
将源数据寄存器中完整的 `八个字节` 存入目标地址指向的内存中，目标地址由 **基址寄存器** 加 **左移三位的有符号立即数偏移** 计算得到。 

## 汇编语法

```asm
    hl.sdi SrcL, [SrcR, simm]
```

## 汇编符号

- **SrcL**：数据寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：有符号立即数偏移，该值除以8后编码在simm22字段中。

## 编码格式

- 低16bit编码：

![HL.SDI](../../../figs/bitfield/svg/Instruction_48bit_16/HL.SDI.svg)

- 高32bit编码：

![HL.SDI](../../../figs/bitfield/svg/Instruction_48bit_32/HL.SDI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);

    bits(64) data = R[m, 64];
    bits(64) baseAddr = R[n, 64];
    bits(64) offset = SignExtend(simm22);

    bits(64) address = baseAddr + (offset << 3);
    Mem[address] = data[63:0];
```

## 汇编索引模式

```asm
hl.sdi a1, [a2, simm]     /* 双寄存器绝对索引 */
hl.sdi a1, [t#2, simm]    /* 双寄存器混合索引 */
hl.sdi a1, [u#2, simm]    /* 双寄存器混合索引 */
hl.sdi t#1, [a2, simm]    /* 双寄存器混合索引 */
hl.sdi t#1, [t#2, simm]   /* 双寄存器相对索引 */
hl.sdi t#1, [u#2, simm]   /* 双寄存器相对索引 */
hl.sdi u#1, [a2, simm]    /* 双寄存器混合索引 */
hl.sdi u#1, [t#2, simm]   /* 双寄存器相对索引 */
hl.sdi u#1, [u#2, simm]   /* 双寄存器相对索引 */
```

## 注意事项

该指令支持地址非对齐访问。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
