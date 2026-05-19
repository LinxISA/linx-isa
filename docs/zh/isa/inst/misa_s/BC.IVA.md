# BC.IVA

## 说明

按虚拟地址无效化块指令缓存(*Invalidate Block Cache by Virtual Address*)  
无效化源寄存器中虚拟地址在块指令缓存 `Block Header Cache` 中对应的缓存行。

## 汇编语法

```
    bc.iva SrcL
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![BC.IVA](../../../figs/bitfield/svg/Instruction_32bit/BC.IVA.svg)

## 汇编索引模式

```asm
bc.iva a1   /* 单寄存器绝对索引 */
bc.iva t#1  /* 单寄存器相对索引 */
bc.iva u#1  /* 单寄存器相对索引 */
```

!!! note "注意"

    该指令不占用块内私有寄存器。

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
