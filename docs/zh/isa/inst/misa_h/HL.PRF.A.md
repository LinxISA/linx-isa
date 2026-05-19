# HL.PRF.A

## 说明

内存预取·写地址(*Prefetch with Address update*)  
由 **基址寄存器值** 加 **偏移寄存器值** 计算得到地址，将包含该地址的 Cache Line 预取到指定的 Cache 中，并将该地址写到目的寄存器中。偏移寄存器值可以有选择的进行移位和扩展。

## 汇编语法

```asm
    hl.prf.a{.l1, .l2, .l3} [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->{t, u, Rd}
```

## 汇编符号

- **.l1,.l2,.l3**：分别表示预取到L1,L2或L3 Cache中。
- **SrcL**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：偏移寄存器，索引范围同SrcL。SrcR可以选择带后缀，分别表示：
    - **.sw**：SignExtendWord，截取操作数低32bit做符号扩展。
    - **.uw**：UnsignedExtendWord，截取操作数低32bit做无符号扩展。
    - **shamt**：对操作数左移位数，范围[0, 7]。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.PRF.A](../../../figs/bitfield/svg/Instruction_48bit_16/HL.PRF.A.svg)

- 高32bit编码：

![HL.PRF.A](../../../figs/bitfield/svg/Instruction_48bit_32/HL.PRF.A.svg)

其中model字段用于编码预取的目标Cache，编码方式如下：

|  model  |   目标Cache    |
|---------|----------------|
|  0    |  L1 Cache    |
|  1    |  L2 Cache    |
|  2    |  L3 Cache    |
|  >2    |  undefined   |

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer datawidth = 64;

    bits(datawidth) baseAddr = R[m, datawidth];
    bits(datawidth) offset = R[n, datawidth];

    case SrcRType of
        when 2b00 then No operation;
        when 2b01 then offset = SignExtend(offset[31:0]);
        when 2b10 then offset = ZeroExtend(offset[31:0]);
        when 2b11 then undefined;

    bits(datawidth) address = baseAddr + (offset << shamt);

    case model of
        when 2b00 then Prefetch(address, target=L1Cache);
        when 2b01 then Prefetch(address, target=L2Cache);
        when 2b10 then Prefetch(address, target=L3Cache);
        otherwise undefined;

    R[d, datawidth] = address;
```

## 汇编索引模式

指令输出到块内t寄存器：
```asm
hl.prf.a.l1 [a1, a2]            ->t          /* 双寄存器绝对索引 */
hl.prf.a.l1 [a1, t#2]           ->t          /* 双寄存器混合索引 */
hl.prf.a.l1 [a1, u#2]           ->t          /* 双寄存器混合索引 */
hl.prf.a.l1 [t#1, a2]           ->t          /* 双寄存器混合索引 */
hl.prf.a.l1 [t#1, t#2]          ->t          /* 双寄存器相对索引 */
hl.prf.a.l1 [t#1, u#2]          ->t          /* 双寄存器相对索引 */
hl.prf.a.l1 [u#1, a2]           ->t          /* 双寄存器混合索引 */
hl.prf.a.l1 [u#1, t#2]          ->t          /* 双寄存器相对索引 */
hl.prf.a.l1 [u#1, u#2]          ->t          /* 双寄存器相对索引 */
hl.prf.a.l2 [a1, a2]            ->t          /* 预取到L2 Cache，支持.l1,.l2,.l3 */
hl.prf.a.l1 [a1, a2.sw]         ->t          /* SrcR寄存器格式转换，支持.sw,.uw */
hl.prf.a.l2 [a1, t#2<<1]        ->t          /* SrcR寄存器小移位，支持移位0-7位 */
hl.prf.a.l2 [a1, u#2.sw<<1]     ->t          /* SrcR寄存器格式转换小移位 */
```

指令输出到块内u寄存器：
```asm
hl.prf.a.l1 [a1, a2]            ->u          /* 双寄存器绝对索引 */
hl.prf.a.l1 [a1, t#2]           ->u          /* 双寄存器混合索引 */
hl.prf.a.l1 [a1, u#2]           ->u          /* 双寄存器混合索引 */
hl.prf.a.l1 [t#1, a2]           ->u          /* 双寄存器混合索引 */
hl.prf.a.l1 [t#1, t#2]          ->u          /* 双寄存器相对索引 */
hl.prf.a.l1 [t#1, u#2]          ->u          /* 双寄存器相对索引 */
hl.prf.a.l1 [u#1, a2]           ->u          /* 双寄存器混合索引 */
hl.prf.a.l1 [u#1, t#2]          ->u          /* 双寄存器相对索引 */
hl.prf.a.l1 [u#1, u#2]          ->u          /* 双寄存器相对索引 */
hl.prf.a.l2 [a1, a2]            ->u          /* 预取到L2 Cache，支持.l1,.l2,.l3 */
hl.prf.a.l1 [a1, a2.sw]         ->u          /* SrcR寄存器格式转换，支持.sw,.uw */
hl.prf.a.l2 [a1, t#2<<1]        ->u          /* SrcR寄存器小移位，支持移位0-7位 */
hl.prf.a.l2 [a1, u#2.sw<<1]     ->u          /* SrcR寄存器格式转换小移位 */
```

指令输出到全局寄存器R1-R23：
```asm
hl.prf.a.l1 [a1, a2]            ->a3          /* 双寄存器绝对索引 */
hl.prf.a.l1 [a1, t#2]           ->a3          /* 双寄存器混合索引 */
hl.prf.a.l1 [a1, u#2]           ->a3          /* 双寄存器混合索引 */
hl.prf.a.l1 [t#1, a2]           ->a3          /* 双寄存器混合索引 */
hl.prf.a.l1 [t#1, t#2]          ->a3          /* 双寄存器相对索引 */
hl.prf.a.l1 [t#1, u#2]          ->a3          /* 双寄存器相对索引 */
hl.prf.a.l1 [u#1, a2]           ->a3          /* 双寄存器混合索引 */
hl.prf.a.l1 [u#1, t#2]          ->a3          /* 双寄存器相对索引 */
hl.prf.a.l1 [u#1, u#2]          ->a3          /* 双寄存器相对索引 */
hl.prf.a.l2 [a1, a2]            ->a3          /* 预取到L2 Cache，支持.l1,.l2,.l3 */
hl.prf.a.l1 [a1, a2.sw]         ->a3          /* SrcR寄存器格式转换，支持.sw,.uw */
hl.prf.a.l2 [a1, t#2<<1]        ->a3          /* SrcR寄存器小移位，支持移位0-7位 */
hl.prf.a.l2 [a1, u#2.sw<<1]     ->a3          /* SrcR寄存器格式转换小移位 */
```

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，仅用于标量块指令块体中。
