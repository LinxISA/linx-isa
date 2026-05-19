# DC.IVA

## 说明

按虚拟地址无效化数据缓存(*Invalidate Data Cache by Virtual Address*)  
无效化源寄存器中虚拟地址在数据缓存 `Data Cache` 中对应的缓存行 `Cacheline`。

## 汇编语法

```
    dc.iva SrcL
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![DC.IVA](../../../figs/bitfield/svg/Instruction_32bit/DC.IVA.svg)

## 汇编索引模式

```asm
dc.iva a1       /* 单寄存器绝对索引 */
dc.iva t#1      /* 单寄存器相对索引 */
dc.iva u#1      /* 单寄存器相对索引 */
```

!!! note "注意"
    
    该指令可能造成未写回数据的丢失，软件应当慎重使用。一般场景下建议使用Clean&Invalidate。
    某些微架构实现允许直接将Invalidate视作Clean&Invalidate。

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
