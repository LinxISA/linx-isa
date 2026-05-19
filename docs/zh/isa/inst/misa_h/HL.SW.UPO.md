# HL.SW.UPO

## 说明

寄存器偏移无缩放·存储字·后索引 (*Store Word with Unscaled Register offset, Post-index*)  
将数据寄存器的低位 `四个字节` 存入 **基址寄存器** 指示的地址内存中，并将 **基址寄存器** 加 **偏移寄存器值** 计算得到的更新地址写到目的寄存器中。偏移寄存器的值可以有选择的进行取低字有符号或无符号扩展。

## 汇编语法

```asm
    hl.sw.upo SrcD, [SrcL, SrcR<{.sw,.uw}>], ->{t, u, Rd}
```

## 汇编符号

- **SrcD**：源数据寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcL**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：偏移寄存器，索引范围同SrcL。SrcR可以选择带后缀，分别表示：
    - **.sw**：截取操作数低32bit做符号扩展。
    - **.uw**：截取操作数低32bit做无符号扩展。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.SW.UPO](../../../figs/bitfield/svg/Instruction_48bit_16/HL.SW.UPO.svg)

- 高32bit编码：

![HL.SW.UPO](../../../figs/bitfield/svg/Instruction_48bit_32/HL.SW.UPO.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer v = UInt(SrcD);

    bits(64) address = R[m, 64];
    bits(64) offset = R[n, 64];
    bits(64) data = R[v, 64];

    case SrcRType of
        when 0b00 : No operation;
        when 0b01 : offset = SignExtend(offset[31:0]);
        when 0b10 : offset = ZeroExtend(offset[31:0]);
        when 0b11 : undefined;

    bits(64) newaddr = address + offset;
    Mem[address] = data[31:0];
    R[d, 64] = newaddr;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
hl.sw.upo a1, [a2, a3]         ->t          /* 三寄存器绝对索引 */
hl.sw.upo a1, [t#2, u#3]       ->t          /* 三寄存器混合索引 */
hl.sw.upo a1, [u#2, t#3]       ->t          /* 三寄存器混合索引 */
hl.sw.upo t#1, [a2, u#3]       ->t          /* 三寄存器混合索引 */
hl.sw.upo t#1, [u#2, a3]       ->t          /* 三寄存器混合索引 */
hl.sw.upo t#1, [t#2, t#3]      ->t          /* 三寄存器混合索引 */
hl.sw.upo u#1, [a2, t#3]       ->t          /* 三寄存器混合索引 */
hl.sw.upo u#1, [t#2, a3]       ->t          /* 三寄存器相对索引 */
hl.sw.upo u#1, [u#2, u#3]      ->t          /* 三寄存器相对索引 */
hl.sw.upo a1, [a2, a3.sw]      ->t          /* SrcR寄存器格式转换，支持.sw,.uw */
hl.sw.upo a1, [a2, t#3.sw]     ->t          /* SrcR寄存器格式转换，支持.sw,.uw */
hl.sw.upo a1, [a2, u#3.sw]     ->t          /* SrcR寄存器格式转换，支持.sw,.uw */
```

指令输出到块内u寄存器：
```asm
hl.sw.upo a1, [a2, a3]         ->u          /* 三寄存器绝对索引 */
hl.sw.upo a1, [t#2, u#3]       ->u          /* 三寄存器混合索引 */
hl.sw.upo a1, [u#2, t#3]       ->u          /* 三寄存器混合索引 */
hl.sw.upo t#1, [a2, u#3]       ->u          /* 三寄存器混合索引 */
hl.sw.upo t#1, [u#2, a3]       ->u          /* 三寄存器混合索引 */
hl.sw.upo t#1, [t#2, t#3]      ->u          /* 三寄存器混合索引 */
hl.sw.upo u#1, [a2, t#3]       ->u          /* 三寄存器混合索引 */
hl.sw.upo u#1, [t#2, a3]       ->u          /* 三寄存器相对索引 */
hl.sw.upo u#1, [u#2, u#3]      ->u          /* 三寄存器相对索引 */
hl.sw.upo a1, [a2, a3.sw]      ->u          /* SrcR寄存器格式转换，支持.sw,.uw */
hl.sw.upo a1, [a2, t#3.sw]     ->u          /* SrcR寄存器格式转换，支持.sw,.uw */
hl.sw.upo a1, [a2, u#3.sw]     ->u          /* SrcR寄存器格式转换，支持.sw,.uw */
```

指令输出到全局寄存器R1-R23：
```asm
hl.sw.upo a1, [a2, a3]         ->a3          /* 三寄存器绝对索引 */
hl.sw.upo a1, [t#2, u#3]       ->a3          /* 三寄存器混合索引 */
hl.sw.upo a1, [u#2, t#3]       ->a3          /* 三寄存器混合索引 */
hl.sw.upo t#1, [a2, u#3]       ->a3          /* 三寄存器混合索引 */
hl.sw.upo t#1, [u#2, a3]       ->a3          /* 三寄存器混合索引 */
hl.sw.upo t#1, [t#2, t#3]      ->a3          /* 三寄存器混合索引 */
hl.sw.upo u#1, [a2, t#3]       ->a3          /* 三寄存器混合索引 */
hl.sw.upo u#1, [t#2, a3]       ->a3          /* 三寄存器相对索引 */
hl.sw.upo u#1, [u#2, u#3]      ->a3          /* 三寄存器相对索引 */
hl.sw.upo a1, [a2, a3.sw]      ->a3          /* SrcR寄存器格式转换，支持.sw,.uw */
hl.sw.upo a1, [a2, t#3.sw]     ->a3          /* SrcR寄存器格式转换，支持.sw,.uw */
hl.sw.upo a1, [a2, u#3.sw]     ->a3          /* SrcR寄存器格式转换，支持.sw,.uw */
```

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
