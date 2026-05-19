# DC.CIVA

## 说明

按虚拟地址清除并无效化数据缓存(*Clean and Invalidate Data Cache by Virtual Address*)  
将源寄存器中的虚拟地址在数据缓存 `Data Cache` 中所对应的缓存行 `Cacheline` 写回到下一级高速缓存或主处理器中，并标记该 `Cacheline` 无效。

## 汇编语法

```
    dc.civa SrcL
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![DC.CIVA](../../../figs/bitfield/svg/Instruction_32bit/DC.CIVA.svg)

## 汇编索引模式

```asm
dc.civa a1       /* 单寄存器绝对索引 */
dc.civa t#1      /* 单寄存器相对索引 */
dc.civa u#1      /* 单寄存器相对索引 */
```

!!! note "注意"

    该指令实现等于先后执行Clean和Invalidate。

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
