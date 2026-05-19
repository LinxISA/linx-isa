# 常量值和立即数

灵犀指令集的微指令的编码长度为16/32/48/64bit。在灵犀指令集中，对于32位的常量值和立即数拆分成高20bit和低12bit两部分，能够将这些常量值和立即数编码到操作码内,或者使用64bit的指令加载立即数。如果是更大位宽的数值，则需要进一步结合ALU指令进行数据的拼接。下面主要介绍针对32/64bit的常量和立即数的指令表达。

用lui或者addtpc指令编码高20bit的数值, 用addi或者subi指令编码低12bit的数值。使用常量值和立即数的取值操作来告诉汇编获取相应值。

立即数：

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

例如将一个0x3fa80赋值到T寄存器，你需要写成:

```
lui 0x3f, ->t
addi t#1,0xa80, ->t
```
或者使用常量值和立即数的取值操作获得立即数的高20bit,低12bit。

```
lui %hi(0x3fa80), ->t
addi t#1,%lo(0x3fa80), ->t
```

常量值：变量的地址，在汇编编程时无法确定，但是在生成最终二进制的时候可以确定，并且这部分地址被编码在指令操作码中，不会变化，因此称之为常量值。

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

例如想要访问一个TLS变量errno，我需要先拿到errno变量相对TP(线程寄存器)的相对地址

```
lui %tprel_hi(errno), ->t        /* 获得errno相对TP寄存器的偏移值  */
ssrget 0x0010, ->t               /* 获得tp系统寄存器的值 */
add t#1,t#2, ->t                 /* TP + OFFSET */ 
addi t#1,%tprel_lo(errno), ->t   /* 获得errno相对TP寄存器的偏移值的低12位， 最终的结果为 TP + OFFSET */

```
