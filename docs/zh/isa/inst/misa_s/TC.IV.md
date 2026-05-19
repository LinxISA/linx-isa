# TLB.IV

## 说明
清除指定虚拟地址的TLB数据(*Translation Lookaside Buffer, Invalidate by Virtual address*)  
清除当前ACR对应翻译级别下，由{SrcL}指定的虚拟地址范围内的TLB数据

## 汇编语法

```
    tlb.iv SrcL
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![TC.IV](../../../figs/bitfield/svg/Instruction_32bit/TC.IV.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) address = R[m, datawidth];

    //清除指定虚拟地址的TLB数据
    TLB.erase(address);
```

## 汇编索引模式

```asm
tlb.iv   a1              /*单寄存器绝对索引*/
tlb.iv   t#1             /*单寄存器相对索引*/
tlb.iv   u#1             /*单寄存器相对索引*/
```

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
