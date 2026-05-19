# C.EBREAK

## 说明

异常中断(*Exception Break*)<br>
本指令通过抛出断点异常 **E_BREAKPOINT** 的方式请求调试器，并将立即数写入[SSR:TRAPNO](../../register/ssr/TRAPNO.md)寄存器的**cause** 字段低位。

本指令的32bit版本请见[EBREAK](../misa_s/EBREAK.md)。

## 汇编语法

```asm
    c.ebreak imm 
```

其中，立即数imm的含义由操作系统定义。

## 编码格式

![C.EBREAK](../../../figs/bitfield/svg/Instruction_16bit/C.EBREAK.svg)

## 汇编示例

```asm
   BSTART
   lui 20,         ->t
   addi a0, t#1,   ->t
   c.ldi [a1, 0],  ->t    <----- c.ebreak 0
   ldi [a0, 8],    ->t                      
   ldi [a1, 0],    ->u
   add t#1, u#1,   ->u          
   BSTART/BSTOP
```

异常响应完成后，重新开启一个块并继承前半部分块的状态，从后半部分块的第一条指令开始继续执行。详见[块指令异常](../../arch/exception.md#blockexception)。
