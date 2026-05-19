# IC.IVA

## 说明

按虚拟地址无效化微指令缓存(*Invalidate Instruction Cache by Virtual Address*)  
无效化源寄存器中虚拟地址在微指令缓存 `Instruction Cache` 中对应的缓存行 `Cacheline`。

## 汇编语法

```
    ic.iva SrcL
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![IC.IVA](../../../figs/bitfield/svg/Instruction_32bit/IC.IVA.svg)

## 汇编索引模式

```asm
ic.iva a1       /* 单寄存器绝对索引 */
ic.iva t#1      /* 单寄存器相对索引 */
ic.iva u#1      /* 单寄存器相对索引 */
```

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
