# HL.LWI

## 说明

立即数偏移·字加载 (*Load Word with Immediate offset*)  
以 **基址寄存器** 加 **左移两位的有符号立即数偏移** 的结果为地址，从内存加载 `四个字节` 的数据并有符号扩展后写到目的寄存器中。

## 汇编语法

```asm
    hl.lwi [SrcL, simm], ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：有符号立即数偏移，该值除以4后编码在simm22字段。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.LWI](../../../figs/bitfield/svg/Instruction_48bit_16/HL.LWI.svg)

- 高32bit编码：

![HL.LWI](../../../figs/bitfield/svg/Instruction_48bit_32/HL.LWI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);

    bits(64) baseAddr = R[s, 64];
    bits(64) offset = SignExtend(simm22);

    bits(64) address = baseAddr + (offset << 2);
    bits(64) data = SignExtend(Mem[address][31:0]);
    
    R[d, 64] = data;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
hl.lwi [a1, simm],     ->t                /* 单寄存器绝对索引 */
hl.lwi [t#1, simm],    ->t                /* 单寄存器相对索引 */
hl.lwi [u#1, simm],    ->t                /* 单寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
hl.lwi [a1, simm],     ->u                /* 单寄存器绝对索引 */
hl.lwi [t#1, simm],    ->u                /* 单寄存器相对索引 */
hl.lwi [u#1, simm],    ->u                /* 单寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
hl.lwi [a1, simm],     ->a3                /* 单寄存器绝对索引 */
hl.lwi [t#1, simm],    ->a3                /* 单寄存器相对索引 */
hl.lwi [u#1, simm],    ->a3                /* 单寄存器相对索引 */
```

## 注意事项

该指令支持地址非对齐访问。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
