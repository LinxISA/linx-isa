# Constant values and immediate values

The encoding length of the microinstruction of LinxISA is 16/32/48/64bit. In LinxISA, 32-bit constant values ​​and immediate values ​​are split into high 20-bit and low 12-bit parts. These constant values ​​and immediate values ​​can be encoded into opcodes, or 64-bit instructions can be used to load the immediate values. If it is a value with a larger bit width, it is necessary to further combine the ALU instructions for data splicing. The following mainly introduces the instruction expressions for 32/64bit constants and immediate numbers.

Use the lui or addtpc instruction to encode the higher 20-bit value, and the addi or subi instruction to encode the lower 12-bit value. Use constant value and immediate value operations to tell the assembly to obtain the corresponding value.

Immediate number:

```
if (0 <= imm <= 4095)
    addi zero,imm, ->t
else if (-4095 <= imm < 0)
    subi zero,-imm, ->t
else if (isInt<32>(imm))
    lui (imm & 0xffffff000), ->t 
    addi t#1,(imm & 0x00000fff), ->t
    /* 或者使用一条64bit指令 */
    l.addli zero,imm, ->t
else 
    subi zero, 1, ->t      /* 需要进行立即数拼接，如表达0xffffffff  */
    zext.w t#1, ->t
```

For example, to assign a value of 0x3fa80 to the T register, you need to write:

```
lui 0x3f, ->t
addi t#1,0xa80, ->t
```
Or use the value operation of constant value and immediate number to obtain the high 20 bits and low 12 bits of the immediate number.

```
lui %hi(0x3fa80), ->t
addi t#1,%lo(0x3fa80), ->t
```

Constant value: The address of a variable cannot be determined during assembly programming, but it can be determined when the final binary is generated, and this part of the address is encoded in the instruction opcode and will not change, so it is called a constant value.

```
if (使用符号绝对地址)
    lui %hi(symbol), ->t      
    addi t#1,%lo(symbol), ->t   
else if (使用符号相对当前TPC的相对地址)
    if (相对地址isInt<32>)
      label:
      addtpc %tpcrel_hi(symbol), ->t    /* 获得symbol的地址相对于当前微指令tpc的偏移值，高20位编码  */
      addi t#1,%tpcrel_lo(label), ->t   /* 获得symbol的地址相对于微指令addtpc的地址（等于标签label的地址）的偏移值，低12位编码  */
    else 
      label:
      addtpc %got_tpcrel_hi(symbol), ->t  /* 获得symbol的GOT表的地址相对于当前微指令tpc的偏移值，高20位编码  */
      addi t#1, %tpcrel_lo(label), ->t    /* 获得symbol的GOT表的地址相对于微指令addtpc的地址（等于标签label的地址）的偏移值，低12位编码  */
else if (对于线程Local的变量，使用符号相对于TP（线程寄存器）的相对地址)
    if（TLS变量的访问,当前仅支持Local Exec的模式）
      lui %tprel_hi(symbol), ->t
      ssrget 0x0010, ->t
      add t#1,t#2, ->t
      addi t#1, %tprel_lo(symbol), ->t
else if (对于全局变量，使用符号相对于GP(全局寄存器)的相对地址)
    if (全局变量的访问)
      lui %gprel_hi(symbol), ->t
      ssrget 0x0011, ->t
      add t#1, t#2, ->t
      addi t#1, %gprel_lo(symbol), ->t
```

For example, if I want to access a TLS variable errno, I need to first get the relative address of the errno variable to TP (thread register)

```
lui %tprel_hi(errno), ->t        /* 获得errno相对TP寄存器的偏移值  */
ssrget 0x0010, ->t               /* 获得tpZXTERMZH6QXZ的值 */
add t#1,t#2, ->t                 /* TP + OFFSET */ 
addi t#1,%tprel_lo(errno), ->t   /* 获得errno相对TP寄存器的偏移值的低12位， 最终的结果为 TP + OFFSET */

```