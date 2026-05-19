# HL.SHI.UPO

## 说明

立即数偏移无缩放·存储半字·后索引 (*Store Halfword with Unscaled Immediate Offset, Post-index*)  
将数据寄存器的低位 `两个字节` 存入 **基址寄存器** 指示的地址内存中，并将 **基址寄存器** 加 **有符号立即数偏移** 计算得到的更新地址写到目的寄存器中。

## 汇编语法

```asm
    hl.shi.upo SrcL, [SrcR, simm], ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：数据寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：有符号立即数，编码在simm17字段中。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.SHI.UPO](../../../figs/bitfield/svg/Instruction_48bit_16/HL.SHI.UPO.svg)

- 高32bit编码：

![HL.SHI.UPO](../../../figs/bitfield/svg/Instruction_48bit_32/HL.SHI.UPO.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);

    bits(64) data = R[m, 64];
    bits(64) address = R[n, 64];
    bits(64) offset = SignExtend(simm17);
    bits(64) newaddr = address + offset;

    Mem[address] = data[15:0];
    R[d, 64] = newaddr;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
hl.shi.upo a1, [a2, simm]          ->t          /* 双寄存器绝对索引 */
hl.shi.upo a1, [t#2, simm]         ->t          /* 双寄存器混合索引 */
hl.shi.upo a1, [u#2, simm]         ->t          /* 双寄存器混合索引 */
hl.shi.upo t#1, [a2, simm]         ->t          /* 双寄存器混合索引 */
hl.shi.upo t#1, [t#2, simm]        ->t          /* 双寄存器相对索引 */
hl.shi.upo t#1, [u#2, simm]        ->t          /* 双寄存器相对索引 */
hl.shi.upo u#1, [a2, simm]         ->t          /* 双寄存器混合索引 */
hl.shi.upo u#1, [t#2, simm]        ->t          /* 双寄存器相对索引 */
hl.shi.upo u#1, [u#2, simm]        ->t          /* 双寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
hl.shi.upo a1, [a2, simm]          ->u          /* 双寄存器绝对索引 */
hl.shi.upo a1, [t#2, simm]         ->u          /* 双寄存器混合索引 */
hl.shi.upo a1, [u#2, simm]         ->u          /* 双寄存器混合索引 */
hl.shi.upo t#1, [a2, simm]         ->u          /* 双寄存器混合索引 */
hl.shi.upo t#1, [t#2, simm]        ->u          /* 双寄存器相对索引 */
hl.shi.upo t#1, [u#2, simm]        ->u          /* 双寄存器相对索引 */
hl.shi.upo u#1, [a2, simm]         ->u          /* 双寄存器混合索引 */
hl.shi.upo u#1, [t#2, simm]        ->u          /* 双寄存器相对索引 */
hl.shi.upo u#1, [u#2, simm]        ->u          /* 双寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
hl.shi.upo a1, [a2, simm]          ->a3          /* 双寄存器绝对索引 */
hl.shi.upo a1, [t#2, simm]         ->a3          /* 双寄存器混合索引 */
hl.shi.upo a1, [u#2, simm]         ->a3          /* 双寄存器混合索引 */
hl.shi.upo t#1, [a2, simm]         ->a3          /* 双寄存器混合索引 */
hl.shi.upo t#1, [t#2, simm]        ->a3          /* 双寄存器相对索引 */
hl.shi.upo t#1, [u#2, simm]        ->a3          /* 双寄存器相对索引 */
hl.shi.upo u#1, [a2, simm]         ->a3          /* 双寄存器混合索引 */
hl.shi.upo u#1, [t#2, simm]        ->a3          /* 双寄存器相对索引 */
hl.shi.upo u#1, [u#2, simm]        ->a3          /* 双寄存器相对索引 */
```

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
