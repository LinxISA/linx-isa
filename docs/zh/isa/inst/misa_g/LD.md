# LD

## 说明

寄存器偏移·双字加载 (*Load Doubleword with Register Offset*)  
以 **基址寄存器**加 **偏移寄存器** 的结果为地址，从内存加载 `八个字节` 的数据后中。偏移寄存器值可以有选择的进行移位和扩展。

## 汇编语法

```c
    ld [SrcL, SrcR<{.sw,.uw}><<<shamt>], ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：偏移寄存器，索引范围同SrcL。SrcR可以选择带后缀，分别表示：
    - **.sw**：截取操作数低32bit做符号扩展。
    - **.uw**：截取操作数低32bit做无符号扩展。
    - **shamt**：对操作数移动位数，范围[0, 31]。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![LD](../../../figs/bitfield/svg/Instruction_32bit/LD.svg)

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
    bits(datawidth) data = Mem[address][63:0];

    R[d, datawidth] = data;
```

## 汇编索引模式

指令输出到块内t寄存器：
```asm
ld [a1, a2],        ->t                /* 双寄存器绝对索引 */
ld [a1, t#2],       ->t                /* 双寄存器混合索引 */
ld [a1, u#2],       ->t                /* 双寄存器混合索引 */
ld [t#1, a2],       ->t                /* 双寄存器混合索引 */
ld [t#1, t#2],      ->t                /* 双寄存器相对索引 */
ld [t#1, u#2],      ->t                /* 双寄存器相对索引 */
ld [u#1, a2],       ->t                /* 双寄存器混合索引 */
ld [u#1, t#2],      ->t                /* 双寄存器相对索引 */
ld [u#1, u#2],      ->t                /* 双寄存器相对索引 */
ld [a1, a2.sw],     ->t                /* SrcR寄存器格式转换，支持.sw,.uw */
ld [a1, t#2<<1],    ->t                /* SrcR寄存器左移，支持左移0-31位。 */
ld [a1, u#2.sw<<1], ->t                /* SrcR寄存器格式转换并左移 */
```

指令输出到块内u寄存器：
```asm
ld [a1, a2],        ->u                /* 双寄存器绝对索引 */
ld [a1, t#2],       ->u                /* 双寄存器混合索引 */
ld [a1, u#2],       ->u                /* 双寄存器混合索引 */
ld [t#1, a2],       ->u                /* 双寄存器混合索引 */
ld [t#1, t#2],      ->u                /* 双寄存器相对索引 */
ld [t#1, u#2],      ->u                /* 双寄存器相对索引 */
ld [u#1, a2],       ->u                /* 双寄存器混合索引 */
ld [u#1, t#2],      ->u                /* 双寄存器相对索引 */
ld [u#1, u#2],      ->u                /* 双寄存器相对索引 */
ld [a1, a2.sw],     ->u                /* SrcR寄存器格式转换，支持.sw,.uw */
ld [a1, t#2<<1],    ->u                /* SrcR寄存器左移，支持左移0-31位。 */
ld [a1, u#2.sw<<1], ->u                /* SrcR寄存器格式转换并左移 */
```

指令输出到全局寄存器R1-R23：
```asm
ld [a1, a2],        ->a3                /* 双寄存器绝对索引 */
ld [a1, t#2],       ->a3                /* 双寄存器混合索引 */
ld [a1, u#2],       ->a3                /* 双寄存器混合索引 */
ld [t#1, a2],       ->a3                /* 双寄存器混合索引 */
ld [t#1, t#2],      ->a3                /* 双寄存器相对索引 */
ld [t#1, u#2],      ->a3                /* 双寄存器相对索引 */
ld [u#1, a2],       ->a3                /* 双寄存器混合索引 */
ld [u#1, t#2],      ->a3                /* 双寄存器相对索引 */
ld [u#1, u#2],      ->a3                /* 双寄存器相对索引 */
ld [a1, a2.sw],     ->a3                /* SrcR寄存器格式转换，支持.sw,.uw */
ld [a1, t#2<<1],    ->a3                /* SrcR寄存器左移，支持左移0-31位。 */
ld [a1, u#2.sw<<1], ->a3                /* SrcR寄存器格式转换并左移 */
```

## 注意事项

该指令支持地址非对齐访问。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
