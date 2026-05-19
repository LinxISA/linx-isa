# IC.IALL

## 说明

无效所有数据缓存(*Invalidate All Instruction Cache*)  
在微指令缓存 `Instruction Cache`中无效化所有的缓存行 `Cacheline`。

## 汇编语法

```
    ic.iall SrcL
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![IC.IALL](../../../figs/bitfield/svg/Instruction_32bit/IC.IALL.svg)

## 汇编索引模式

```asm
ic.iall a1       /* 单寄存器绝对索引 */
ic.iall t#1      /* 单寄存器相对索引 */
ic.iall u#1      /* 单寄存器相对索引 */
```

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
