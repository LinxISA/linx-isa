# TLB.IALL

## 说明
清除所有TLB数据(*Translation Lookaside Buffer, Invalidate All*)  
用来清除所有的TLB数据。

## 汇编语法

```
    tlb.iall
```

## 编码格式

![TC.IALL](../../../figs/bitfield/svg/Instruction_32bit/TC.IALL.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    //清除所有的TLB数据
    TLB.clear();
```

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
