# SB

## 说明

寄存器偏移·存字节(*Store Byte with Register Offset*)  
将源数据寄存器的低位 `一个字节` 存入目标地址指向的内存。目标地址由 **基址寄存器** 加 **偏移寄存器** 计算得到，偏移寄存器的值可以有选择的进行取低字有或无符号扩展。

## 汇编语法

```c
    sb SrcD, [SrcL, SrcR<{.sw,.uw}>]
```

## 汇编符号

- **SrcD**：数据寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcL**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：偏移寄存器，索引范围同SrcL。SrcR可以选择带后缀，分别表示：
    - **.sw**：截取操作数低32bit做符号扩展。
    - **.uw**：UnsignedExtendWord，截取操作数低32bit做无符号扩展。

## 编码格式

![SB](../../../figs/bitfield/svg/Instruction_32bit/SB.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer v = UInt(SrcD);
    integer datawidth = 64;

    bits(datawidth) baseAddr = R[m, datawidth];
    bits(datawidth) offset   = R[n, datawidth];
    bits(datawidth) data     = R[v, datawidth];

    case SrcRType of
        when 2b00 then No operation;
        when 2b01 then offset = SignExtend(offset[31:0]);
        when 2b10 then offset = ZeroExtend(offset[31:0]);
        when 2b11 then undefined;

    bits(datawidth) address = baseAddr + offset;
    Mem[address] = data[7:0];
```

## 汇编索引模式

```asm
sb a1, [a2, a3]        /* 三寄存器绝对索引 */
sb a1, [t#2, u#3]      /* 三寄存器混合索引 */
sb a1, [u#2, t#3]      /* 三寄存器混合索引 */
sb t#1, [a2, u#3]      /* 三寄存器混合索引 */
sb t#1, [u#2, a3]      /* 三寄存器混合索引 */
sb t#1, [t#2, t#3]     /* 三寄存器相对索引 */
sb u#1, [a2, t#3]      /* 三寄存器混合索引 */
sb u#1, [t#2, a3]      /* 三寄存器混合索引 */
sb u#1, [u#2, u#3]     /* 三寄存器相对索引 */
sb a1, [a2, a3.sw]     /* SrcR寄存器格式转换，支持.sw,.uw */
sb a1, [a2, t#3.sw]    /* SrcR寄存器格式转换，支持.sw,.uw */
sb a1, [a2, u#3.sw]    /* SrcR寄存器格式转换，支持.sw,.uw */
```

## 注意事项

本指令不占块内私有寄存器槽位。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
