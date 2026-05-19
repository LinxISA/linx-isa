# EBREAK

## 说明

异常中断(*Exception Break*)<br>
本指令通过抛出断点异常 **E_BREAKPOINT** 的方式请求调试器，并将立即数写入[SSR:TRAPNO](../../register/ssr/TRAPNO.md)寄存器的**cause** 字段低位。

## 汇编语法

```asm
    ebreak imm 
```

其中，立即数imm的含义由操作系统定义。

## 编码格式

![EBREAK](../../../figs/bitfield/svg/Instruction_32bit/EBREAK.svg)

## 汇编示例

示例一：断点打在块内微指令上，观察前序微指令执行后的状态。
```asm
   BSTART
   lui 20,       ->t
   addi a0, t#1, ->t
   ld [a1, t#1],  ->t    <----- ebreak imm
   ldi [a0, 8],   ->t                      
   ldi [a1, 0],  ->u
   add t#1, u#1, ->u          
   BSTART/BSTOP
```

示例二：断点打在当前块的提交指令上，观察本块所有指令执行后的状态
```asm
   BSTART
   lui 20,      ->t
   addi a0, t#1, ->t    
   ld [a1, t#1], ->t    
   ldi [a0, 8],  ->t    
   BSTART/BSTOP     <---- ebreak imm
    ...
```

示例三：断点打在块头指令上，只能观察到块间状态。
```asm
   BSTART
   lui 20,       ->t
   addi a0, t#1, ->t
   ld [a1, t#1],  ->t
   ldi [a0, 8],   ->t                      
   ldi [a1, 0],  ->u
   add t#1, u#1, ->u          
   BSTART/BSTOP
   B.CATR                <----- ebreak imm
   addi a0, a1 ->t
```

异常响应完成后，重新开启一个块并继承前半部分块的状态，从后半部分块的第一条指令开始继续执行。详见[块指令异常](../../arch/exception.md#blockexception)。
