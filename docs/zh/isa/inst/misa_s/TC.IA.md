# TLB.IA

## 说明
清除指定ASID的TLB数据(*Translation Lookaside Buffer, Invalidate by ASID*)  
用来清除指定ASID（地址空间标识符，用于区分非全局的虚拟内存页）相关的TLB数据, 由{SrcL}指定ASID。

## 汇编语法

```
    tlb.ia SrcL
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![TLB.IA](../../../figs/bitfield/svg/Instruction_32bit/TC.IA.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) ASID = R[m, datawidth];

    //清除指定ASID相关的TLB数据
    TLB.erase(ASID);
```

## 汇编索引模式

```asm
tlb.ia   a1              /*单寄存器绝对索引*/
tlb.ia   t#1             /*单寄存器相对索引*/
tlb.ia   u#1             /*单寄存器相对索引*/
```

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
