# DMA

## 说明

直接内存存取(*Direct Memory Access*)<br>
从源地址指示的内存起始位置拷贝 64 字节大小的数据到目的地址指示的内存空间中。

## 汇编语法

```asm
    dma SrcL, SrcR
```

## 汇编符号

- **SrcL**：源寄存器，用于存储源地址。可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：源寄存器，用于存储目的地址。可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 指令编码

![DMA](../../../figs/bitfield/svg/Instruction_32bit/DMA.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer l = UInt(SrcL);
    integer r = UInt(SrcR);

    bits(64) src_address = R[l, 64];
    bits(64) dst_address = R[r, 64];
    
    bits(512) data = Mem[src_address];
    Mem[dst_address] = data;
```

## 备注

本指令用于[MCOPY.D](../../header/templateblock/MCOPY.D.md)模版块进行64字节数据拷贝。
