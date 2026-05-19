# TLB.IAV

## 说明
清除指定ASID和虚拟地址的所有TLB数据(*Translation Lookaside Buffer, Invalidate by ASID and Virtual address*)  
清除当前ACR翻译级别下，{SrcL}指定ASID和虚拟地址范围的TLB数据

## 汇编语法

```
    tlb.iav SrcL
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

其中：

- SrcL[44:0]：用于存储虚拟地址。
- SrcL[63:48]：用于存储ASID。

## 编码格式

![TC.IAV](../../../figs/bitfield/svg/Instruction_32bit/TC.IAV.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);

    bits(64) operand = R[m, datawidth];
    bits(16) ASID = operand[63:48];
    bits(45) address = operand[44:0];

    //清除指定ASID和虚拟地址的TLB数据
    TLB.erase(ASID, address);
```

## 汇编索引模式

```asm
tlb.iva   a1              /*单寄存器绝对索引*/
tlb.iva   t#1             /*单寄存器相对索引*/
tlb.iva   u#1             /*单寄存器相对索引*/
```

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
