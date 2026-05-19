# DC.CVA

## 说明

按虚拟地址清除数据缓存(*Data Cache Clean Virtual Address*)  
将源寄存器中的虚拟地址在数据缓存 `Data Cache` 中所对应的缓存行 `Cacheline` 写回到下一级高速缓存或主处理器中。

## 汇编语法

```
    dc.cva SrcL
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![DC.CVA](../../../figs/bitfield/svg/Instruction_32bit/DC.CVA.svg)

## 汇编索引模式

```asm
dc.cva a1       /* 单寄存器绝对索引 */
dc.cva t#1      /* 单寄存器相对索引 */
dc.cva u#1      /* 单寄存器相对索引 */
```

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
