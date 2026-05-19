# HL.SBP

## 说明

存储一对字节(*Store Pair of Byte*)  
将两个数据寄存器的低位 `一个字节` 依次存入目标地址指向的内存中。目标地址由 **基址寄存器** 加 **偏移寄存器** 计算得到，偏移寄存器的值可以有选择的进行取低字有符号或无符号扩展。

## 汇编语法

```asm
    hl.sb SrcD0, SrcD1, [SrcL, SrcR<{.sw,.uw}>]
```

## 汇编符号

- **SrcD0**：第一个数据寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcD1**：第二个数据寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcL**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：偏移寄存器，索引范围同SrcL。SrcR可以选择带后缀，分别表示：
    - **.sw**：截取操作数低32bit做符号扩展。
    - **.uw**：UnsignedExtendWord，截取操作数低32bit做无符号扩展。

## 编码格式

- 低16bit编码：

![HL.SBP](../../../figs/bitfield/svg/Instruction_48bit_16/HL.SBP.svg)

- 高32bit编码：

![HL.SBP](../../../figs/bitfield/svg/Instruction_48bit_32/HL.SBP.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer v1 = UInt(SrcD0);
    integer v2 = UInt(SrcD1);

    bits(64) baseAddr = R[m, 64];
    bits(64) offset = R[n, 64];
    bits(64) data1 = R[v1, 64];
    bits(64) data2 = R[v2, 64];

    case SrcRType of
        when 0b00 : No operation;
        when 0b01 : offset = SignExtend(offset[31:0]);
        when 0b10 : offset = ZeroExtend(offset[31:0]);
        when 0b11 : undefined;

    bits(64) address = baseAddr + offset;
    Mem[address] = data1[7:0];
    Mem[address+1] = data2[7:0];
```

## 汇编索引模式

| SrcD0 | SrcD1 | SrcL | SrcR |
|-------|--------|--------|----------|
| r0-r23 | r0-r23 | r0-r23 |  r0-r23, r0.sw-r23.sw, r0.uw-r23.uw |
| t#1-t#4 | t#1-t#4 | t#1-t#4 |  t#1-t#4, t#1.sw-t#4.sw, t#1.uw-t#4.uw |
| u#1-u#4 | u#1-u#4 | u#1-u#4 |  u#1-u#4, u#1.sw-u#4.sw, u#1.uw-u#4.uw |

## 注意事项

本指令不占块内私有寄存器槽位。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
