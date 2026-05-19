# HL.LWU.PCR

## 说明

PC相对寻址·字加载 (*Load Unsigned Word with PC-Relative*)  
以 **当前TPC** 加 **有符号立即数偏移** 的结果为地址，从内存加载 `四个字节` 的数据并无符号扩展后写到目的寄存器中。

## 汇编语法

```asm
    hl.lwu.pcr [symbol], ->{t, u, Rd}
```

## 汇编符号

- **symbol**：表示加载数据的程序标签，它相对于本指令TPC的距离编码于simm字段。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.LWU.PCR](../../../figs/bitfield/svg/Instruction_48bit_16/HL.LWU.PCR.svg)

- 高32bit编码：

![HL.LWU.PCR](../../../figs/bitfield/svg/Instruction_48bit_32/HL.LWU.PCR.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);

    bits(64) offset = SignExtend(simm);
    bits(64) address = current_tpc + offset;    // current_tpc为当前指令TPC
    bits(64) data = ZeroExtend(Mem[address][31:0]);
    
    R[d, 64] = data;
```

## 汇编索引模式

```asm
hl.lwu.pcr [symbol],    ->t                /* 指令输出到块内t寄存器 */
hl.lwu.pcr [symbol],    ->u                /* 指令输出到块内u寄存器 */
hl.lwu.pcr [symbol],    ->a3               /* 指令输出到全局寄存器R1-R23 */
```

## 注意事项

本指令支持地址非对齐访问。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
