# SIMT command

SIMT instructions can only be used in SIMT blocks. Operation types include: covering existing scalar operations, reduce operations, floating point operations, and diverge processing operations. The register operands of SIMT instructions all need to be expressed in bit width. The general assembly format is as follows:

```
Opcode                                                            /*表示指令无输出*/
Opcode Operand0.<T>, ->{LL_GPR, UL_GPR}.<T>                       /*输出到块内寄存器，SIMT块中有U/T/M/N四组刻度尺寄存器*/
Opcode Operand0.<T>, Operand1.<T>                                 /*表示指令无输出*/
Opcode Operand0.<T>, Operand1.<T>, ->{LL_GPR}.<T>                 /*输出到块内寄存器，SIMT块中有U/T/M/N四组刻度尺寄存器*/
Opcode Operand0.<T>, Operand1.<T>, Operand2.<T>                   /*表示指令无输出*/
Opcode Operand0.<T>, Operand1.<T>, Operand2.<T>, ->{LL_GPR}.<T>   /*输出到块内寄存器，SIMT块中有U/T/M/N四组刻度尺寄存器*/
Opcode Operand0.<T>, Operand1.<T>, Operand2, Operand3             /*表示指令无输出*/
```

In general, the bit width expressions of input and output register operands include:

- '.fd': Input bit width identifier, indicating that the input is a double-precision floating point type with a bit width of 64 bits.
- '.fs': Input bit width identifier, indicating that the input is a single-precision floating point type with a bit width of 32 bits.
- '.fh': Input bit width identifier, indicating that the input is a half-precision floating point type with a bit width of 16 bits.
- '.fb': Input bit width identifier, indicating that the input is an fp8 floating point type with a bit width of 8 bits.
- '.bf': Input bit width identifier, indicating that the input is a bf16 floating point type with a bit width of 16 bits.
- '.flb': Input bit width identifier, indicating that the input is an fp8.1 floating point type with a bit width of 8 bits.
- '.ud': Input bit width identifier, indicating that the input is an unsigned integer with a bit width of 64 bits.
- '.uw': Input bit width identifier, indicating that the input is an unsigned integer with a bit width of 32 bits.
- '.uh': Input bit width identifier, indicating that the input is an unsigned integer with a bit width of 16 bits.
- '.ub': Input bit width identifier, indicating that the input is an unsigned integer with a bit width of 8 bits.
- '.sd': Input bit width identifier, indicating that the input is a signed integer with a bit width of 64 bits.
- '.sw': Input bit width identifier, indicating that the input is a signed integer with a bit width of 32 bits.
- '.sh': Input bit width identifier, indicating that the input is a signed integer with a bit width of 16 bits.
- '.sb': Input bit width identifier, indicating that the input is a signed integer with a bit width of 8 bits.
- '.d': Output bit width identifier, indicating that the output bit width is 64bit.
- '.w': Output bit width identifier, indicating that the output bit width is 32bit.
- '.h': Output bit width identifier, indicating that the output bit width is 16bit.
- '.b': Output bit width identifier, indicating that the output bit width is 8 bits.


For **cvt** class instructions, the input and output bit width identification range is: .fd, .fs, .fh, .fb, .bf, .flb, .ud, .uw, .uh, .ub, .sd, .sw, .sh, .sb. For example:

```
fcvt t#1.fs, ->t.fd                   /*浮点类型间的转换，将单精度浮点数转换成双精度浮点数*/
fcvti t#1.fh, ->t.sw                  /*浮点到整型的转换，将半精度浮点数转换成有符号字*/
icvt t#1.uh, ->t.sw                   /*整型类型间的转换，将无符号半字转换成有符号字*/
icvtf t#1.sw, ->t.fs                  /*整型到浮点的转换，将有符号半字转成成单精度浮点数*/
```

**Usage restrictions:**- Instructions output to global registers are currently limited to reduction instructions, and the output bit width of this type of microinstruction is limited to 64 bits. If the protocol access is required, the corresponding protocol access command must be used.
- The global register represents the scalar value, which is a constant for the SIMT block, while the register within the block represents the vector value, that is, the value within the block can change.
- The input bit width identifier of floating point operands needs to be **.fd, .fs, .fh, .fb, .bf, .flb**, and the input bit width identifier of integer operands needs to be **.ud, .uw, .uh, .ub, .sd, .sw, .sh, .sb**. (1)
- For non-memory access integer operation microinstructions, the register operands need to carry bit width information and the bit width information of the register operands needs to be consistent. The current assembly requires that **the input bit width identifiers are consistent**. Microinstructions with inconsistent bit width identifiers have unpredictable running behavior. At the same time, the input bit width identifiers correspond to the output bit width identifiers. (1)
- For memory access microinstructions, the bit width of the base address part of address calculation defaults to 64 bits, and the bit width of the address offset part is not limited. The output bit width of the memory access read instruction is consistent with the data bit width loaded by the memory access instruction, and the data register bit width of the memory access write instruction is consistent with the data bit width to be stored by the memory access instruction. (2)
- When the current microinstruction directly refers to the result of the previous microinstruction, the bit width needs to be kept consistent, otherwise the execution result will be unpredictable. (3)
- However, for sign-sensitive operations, the use of the main sign bit is required when using the input bit width identifier. When the operation result is inconsistent with the output bit width identifier, and the input bit width is smaller than the output bit width, the corresponding expansion operation is performed according to the sign of the input bit width identifier. (4)
- When there are branches in SIMTblock instruction, you need to use the microinstruction guarantee function related to SIMT stack. (5)
- Except for the address calculation of memory access instructions/**cvt** class microinstructions/floating point microinstructions, the bit width identifier contains the meaning of data type. In other scenarios, it is only used for bit width expression.
- LC, LBsystem register can be indexed directly using SIMT instructions.


For detailed microinstructions, please refer to the chapter [vector instructions] (../../isa/blockIntro/vecinstrs/instIntro.md) in the manual.

Basic instruction example:

(0) Reduce operation assembly diagram

```
rdadd t#1.uh, ->x1.d                   /*寄存器reduce指令，将SIMT块中所有线程的rdadd中16位宽的t#1的值累加，最终的累加值无符号扩展到64bit，写到x1寄存器中*/
rdadd t#1.sw, ->x1.d                   /*寄存器reduce指令，将SIMT块中所有线程的rdadd中32位宽的t#1的值累加，最终的累加值有符号扩展到64bit，写到x1寄存器中*/
sw.add.rd [t#1.d], t#2.w               /*访存reduce指令，将SIMT块中所有线程的sw.add对应的t#2.w的值累加，再与访存地址t#1中的值累加，再存回地址t#1中*/
```

(1) Assembly diagram of arithmetic and logic operations

```
add t#1.sw, t#2.sw, ->t.w              /*将整型的32bit的t#1与32bit的t#2相加写到t刻度尺寄存器中，且输出位宽为32bit，汇编要求用sw表示输入位宽时，都采用sw*/
add a0.uw, t#2.uw, ->t.w               /*uw的写法与sw的写法，输入位宽表达上含义一致*/
fadd t#1.fs, t#2.fs, ->t.w             /*两个单精度浮点数相加，结果写到t刻度尺寄存器中，输出位宽为32bit，输入位宽与输出位宽对应*/
```

(2) Assembly instructions for memory access operations

```
lb [a0.sd, t#1.sw], ->t.b              /*基址a0的位宽要求64bit，地址偏移t#1由32bit有符号扩展到64bit后与基址相加得到64bit访存地址，目的寄存器位宽与lb的加载的数据位宽一致，为8bit*/
lw [a1.sd, t#1.sb], ->t.w              /*基址a1的位宽要求64bit，地址偏移t#1由8bit有符号扩展到64bit后与基址相加得到64bit访存地址，目的寄存器位宽与lw的加载的数据位宽一致，为32bit*/
sw t#1.sw, [a2.ud, lc0.ud]             /*sw微指令的数据寄存器位宽与sw的存储数据位宽一致，均为32bit宽度*/ 
icvt t#1.sw, ->t.sd
sd t#1.sd, [a3.sd, t#2.sb]             /*sd微指令的数据寄存器位宽为64bit，因此需要先将lw的结果通过icvt转换成64bit宽度后才能使用*/
```
(3) There are dependency assembly instructions between instructions

```
sub t#1.sw, t#2.sw, ->t.w
add a0.sw, t#1.sw, ->t.w              /*add指令使用sub的结果，保持位宽都是32bit*/
icvt t#1.sw, ->t.sd
and t#1.sd, x1.sd, ->t.d              /索引前序指令的结果时，需要位宽一致，and使用add的结果，为保持位宽一致，需要使用icvt指令进行转换，将32bit的位宽转成64bbit*/
```

(4)

```
div t#1.sw, t#2.sw, ->t.w             /*位宽为32bit的有符号除法操作*/
div t#1.uw, t#2.uw, ->t.w             /*位宽为32bit的无符号除法操作*/
mul t#1.sd, t#2.sd, ->t.d             /*位宽为64bit的有符号乘法*/
mul t#1.ud, t#2.ud, ->t.d             /*位宽为64bit的无符号乘法*/
```

(5) dive command instructions:

In order to handle the diverge situation in the parallel block, you need to pay attention to the increase in the label of the convergence point of the conditional instruction in the block and the pc.pop of the convergence point. All conditional jump instructions in the current block, including integer comparison jumps and floating point comparison jumps, require label descriptions of the convergence points. For convergence point addresses or jump target addresses that exceed the encoding range, the compiler will convert them to **b.cond** for processing.

```
...
lw [a1.ud, lc0.ud<<2], ->t.w    
b.eq t#1.sw, t#2.sw, _block_D, _converge_E_   /*指示该分支的converge点为_converge_E_*/ 
addi zero.uw, 2, ->m.w
j _converge_E
_block_D:
addi zero.uw, 1, ->u.w
_converge_E:
pc.pop                                       /*converge点pop决定是否还有另一侧的分支待执行，还是顺序往下执行*/
...
```