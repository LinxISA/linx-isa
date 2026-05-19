# C.MOVR

## 说明

寄存器移动(*Move Register*)  
将源寄存器值移动到目的寄存器中。

## 汇编语法

```c
    c.movr SrcL, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![c.movr](../../../figs/bitfield/svg/Instruction_16bit/C.MOVR.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer DataWidth = 64;

    bits(DataWidth) data = R[s, DataWidth];
    R[d, DataWidth] = data;
```

## 汇编索引模式

- 指令输出到块内T寄存器
```asm
    c.movr  a1,   ->t
    c.movr  t#1,  ->t
    c.movr  u#1,  ->t
```

- 指令输出到块内U寄存器
```asm
    c.movr  a1,   ->u
    c.movr  t#1,  ->u
    c.movr  u#1,  ->u
```

- 指令输出到全局寄存器R1-R23
```asm
    c.movr  a1,   ->a3
    c.movr  t#1,  ->a3
    c.movr  u#1,  ->a3
```

!!! info "注意"

    允许源和目的寄存器为同一个寄存器。

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
