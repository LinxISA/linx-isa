# ISB

## 说明

同步指令流(*Fence Instruction Stream*)  
该指令用于同步指令流，使对内存指令区域的读写，对后续取指令操作可见。

## 汇编语法

	isb

## 编码格式

![ISB](../../../figs/bitfield/svg/Instruction_32bit/ISB.svg)

## 执行方式

```
    Fence(Store, Fetch)
```

!!! note "注意"

    该指令不占用块内私有寄存器。

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
