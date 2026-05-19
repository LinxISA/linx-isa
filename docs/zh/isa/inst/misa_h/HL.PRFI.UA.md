# HL.PRFI.UA

## 说明

立即数偏移无缩放·内存预取·写地址(*Prefetch with Unscaled Immediate offset with Address update*)  
由 **基址寄存器值** 加 **有符号立即数偏移** 计算得到地址，将包含该地址的 Cache Line 预取到指定的 Cache中，并将该地址写到目的寄存器中。

## 汇编语法

```asm
    hl.prfi.ua{.l1, .l2, .l3} [SrcL, simm], ->{t, u, Rd}
```

## 汇编符号

- **.l1,.l2,.l3**：分别表示预取到L1,L2或L3 Cache中。
- **SrcL**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：有符号立即数，编码在simm17字段中。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.PRFI.UA](../../../figs/bitfield/svg/Instruction_48bit_16/HL.PRFI.UA.svg)

- 高32bit编码：

![HL.PRFI.UA](../../../figs/bitfield/svg/Instruction_48bit_32/HL.PRFI.UA.svg)

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

    R[d, 64] = address;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
hl.prf.ua.l1 [a1, simm]            ->t          /* 单寄存器绝对索引 */
hl.prf.ua.l2 [t#1, simm]           ->t          /* 单寄存器相对索引 */
hl.prf.ua.l3 [u#1, simm]           ->t          /* 单寄存器相对索引 */
```

指令输出到块内u寄存器:
```asm
hl.prf.ua.l1 [a1, simm]            ->u          /* 双寄存器绝对索引 */
hl.prf.ua.l2 [t#1, simm]           ->u          /* 双寄存器相对索引 */
hl.prf.ua.l3 [u#1, simm]           ->u          /* 双寄存器相对索引 */
```

指令输出到全局寄存器R1-R23:
```asm
hl.prf.ua.l1 [a1, simm]            ->a3          /* 双寄存器绝对索引 */
hl.prf.ua.l2 [t#1, simm]           ->a3          /* 双寄存器相对索引 */
hl.prf.ua.l3 [u#1, simm]           ->a3          /* 双寄存器相对索引 */
```

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，仅用于标量块指令块体中。
