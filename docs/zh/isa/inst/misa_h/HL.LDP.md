# HL.LDP

## 说明

寄存器偏移·一对双字加载 (*Load Pair of Doubleword*)  
以 **基址寄存器** 加 **偏移寄存器** 的结果为地址，从内存连续加载两个 `八字节` 的数据后分别写入两个目的寄存器中。偏移寄存器值可以有选择的进行移位和扩展。

## 汇编语法

```asm
    hl.ldp [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->Dst0, Dst1
```

## 汇编符号

- **SrcL**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：偏移寄存器，索引范围同SrcL。SrcR可以选择带后缀，分别表示：
    - **.sw**：截取操作数低32bit做符号扩展。
    - **.uw**：截取操作数低32bit做无符号扩展。
    - **shamt**：对操作数移动位数，范围[0, 31]。
- **->**：用于指示目的寄存器。
- **Dst0**：第一个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。
- **Dst1**：第二个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.LDP](../../../figs/bitfield/svg/Instruction_48bit_16/HL.LDP.svg)

- 高32bit编码：

![HL.LDP](../../../figs/bitfield/svg/Instruction_48bit_32/HL.LDP.svg)

其中，SrcRType域编码如下：

|  SrcRType  |  汇编标识  |  解释                       |
|-----------|-----------|-----------------------------|
|  00  |   无   |  无格式转换   |
|  01  |  .sw   |  signed extended word，截取操作数的低32bit做有符号扩展  |
|  10  |  .uw   |  unsigned extended word，截取操作数的低32bit做无符号扩展  |
|  11  |  reserve  |  保留  |

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d0 = UInt(RegDst0);
    integer d1 = UInt(RegDst1);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);

    bits(64) baseaddr = R[m, 64];
    bits(64) offset = R[n, 64];

    case SrcRType of
        when 0b00 : offset = No operation;
        when 0b01 : offset = SignExtend(offset[31:0]);
        when 0b10 : offset = ZeroExtend(offset[31:0]);
        when 0b11 : undefined;

    bits(64) address = baseaddr + (offset << shamt);
    bits(128) doubledata = Mem[address][127:0];

    R[d0, 64] = doubledata[63:0];
    R[d1, 64] = doubledata[127:64];
```

## 汇编索引模式

输入输出可选组合如下：

| 输入组合 | 输出组合 |
|---------|-----------|
| **a1, a2**  | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **a1, t#2** | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **a1, u#2** | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **t#1, a2**  | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **t#1, t#2** | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **t#1, u#2** | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **u#1, a2**  | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **u#1, t#2** | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |
| **u#1, u#2** | t, t；t, u；t, a3；u, t；u, u；u, a3；a3, t；a3, u；a3, a4 |

## 注意事项

1. 本指令支持地址非对齐访问。
2. 如果两个目的寄存器相同，那么执行结果不可知（硬件决定保留哪个结果）。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
