# HL.PRFI.U

## 说明

立即数偏移无缩放·内存预取 (*Prefetch with Unscaled Immediate offset*)  
由 **基址寄存器** 加 **有符号立即数偏移** 计算得到地址，将包含该地址的 Cache Line 预取到指定的 Cache中。

## 汇编语法

```asm
    hl.prfi.u{.l1, .l2, .l3} [SrcL, simm]
```

## 汇编符号

- **.l1,.l2,.l3**：分别表示预取到L1,L2或L3 Cache中。
- **SrcL**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：有符号立即数，编码在simm17字段中。

## 编码格式

- 低16bit编码：

![HL.PRFI.U](../../../figs/bitfield/svg/Instruction_48bit_16/HL.PRFI.U.svg)

- 高32bit编码：

![HL.PRFI.U](../../../figs/bitfield/svg/Instruction_48bit_32/HL.PRFI.U.svg)

其中model字段用于编码预取的目标Cache，编码方式如下：

|  model  |   目标Cache    |
|--------|----------------|
|  0    |  L1 Cache    |
|  1    |  L2 Cache    |
|  2    |  L3 Cache    |
|  >2    |  undefined   |

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);

    bits(64) baseAddr = R[s, 64];
    bits(64) offset = SignExtend(simm17);

    bits(64) address = baseAddr + offset;

    case model of
        when 2b00 then Prefetch(address, target=L1Cache);
        when 2b01 then Prefetch(address, target=L2Cache);
        when 2b10 then Prefetch(address, target=L3Cache);
        otherwise undefined;
```

## 汇编索引模式

```asm
hl.prfi.u.l1 [a1, simm]                 /* 单寄存器绝对索引 */
hl.prfi.u.l2 [t#1, simm]                /* 单寄存器相对索引 */
hl.prfi.u.l3 [u#1, simm]                /* 单寄存器相对索引 */
```

## 注意事项

该指令不占用块内私有寄存器。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，仅用于标量块指令块体中。
