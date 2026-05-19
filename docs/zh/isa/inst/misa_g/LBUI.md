# LBUI

## 说明

立即数偏移·无符号字节加载 (*Load Unsigned Byte with Immediate Offset*)  
以 **基址寄存器** 加 **有符号立即数偏移** 的结果为地址，从内存加载 `一个字节` 的数据并无符号扩展（即零扩展）后写到目的寄存器中。

## 汇编语法

```c
    lbui [SrcL, simm], ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：有符号立即数偏移，是-2048到+2047范围内的数，在simm12字段中编码。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![LBUI](../../../figs/bitfield/svg/Instruction_32bit/LBUI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) baseAddr = R[s, datawidth];
    bits(datawidth) offset = SignExtend(simm12);

    bits(datawidth) address = baseAddr + offset;
    bits(datawidth) data = ZeroExtend(Mem[address][7:0]);
    
    R[d, datawidth] = data;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
lbui [a1, simm],     ->t                /* 单寄存器绝对索引 */
lbui [t#1, simm],    ->t                /* 单寄存器相对索引 */
lbui [u#1, simm],    ->t                /* 单寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
lbui [a1, simm],     ->u                /* 单寄存器绝对索引 */
lbui [t#1, simm],    ->u                /* 单寄存器相对索引 */
lbui [u#1, simm],    ->u                /* 单寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
lbui [a1, simm],     ->a3                /* 单寄存器绝对索引 */
lbui [t#1, simm],    ->a3                /* 单寄存器相对索引 */
lbui [u#1, simm],    ->a3                /* 单寄存器相对索引 */
```

## 注意事项

该指令支持地址非对齐访问。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
