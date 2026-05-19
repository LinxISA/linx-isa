# DC.ZVA

## 说明

按虚拟地址将数据缓存清零(*Zero Data Cache Virtual Address*)  
在数据缓存 `Data Cache` 中将SrcL中所表明的 `Cacheline` 全部清零，并写回到下一级高速缓存或主处理器中。

本条指令用于CodeTemplate的MEMSET。

## 汇编语法

```
    dc.zva SrcL
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![DC.ZVA](../../../figs/bitfield/svg/Instruction_32bit/DC.ZVA.svg)

## 汇编索引模式

```asm
dc.zva a1       /* 单寄存器绝对索引 */
dc.zva t#1      /* 单寄存器相对索引 */
dc.zva u#1      /* 单寄存器相对索引 */
```

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
