# DC.CSW

## 说明

数据缓存清除缓存行(*Clean Data Cache by Set/Way*)  
在数据缓存 `Data Cache` 中将源寄存器中所表明的Set/Way对应的 `Cacheline` 写回到下一级高速缓存或主处理器中。

## 汇编语法

```
    dc.csw SrcL
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![DC.CSW](../../../figs/bitfield/svg/Instruction_32bit/DC.CSW.svg)

## 汇编索引模式

```asm
dc.csw a1       /* 单寄存器绝对索引 */
dc.csw t#1      /* 单寄存器相对索引 */
dc.csw u#1      /* 单寄存器相对索引 */
```

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
