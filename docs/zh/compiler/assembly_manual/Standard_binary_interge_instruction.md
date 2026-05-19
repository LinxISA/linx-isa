# 标准二进制整数运算

通常有左源以及右源两个输入的操作对象，一个输出。

```
Opcode Operand0,Operand1,->{LL_GPR, UL_GPR}        /* 输出到块内寄存器或者全局寄存器 */
```

- 在Opcode后面加上‘w’表明进行低32bit有符号扩展<br>
- 在Opcode后面加上‘i'表明右源操作对象为立即数<br>
- 对于算术指令，可以在右源寄存器后加上{.sw, .uw, .neg}扩展，’sw‘表示截取该操作数的低32bit做有符号扩展，’uw‘表示截取该操作数的低32bit做无符号扩展，’neg‘表示对该操作数位取反加1<br>
- 对于逻辑逻辑操作， 可以在右源寄存器后加上{.sw, .uw, .not}扩展， ’.not‘表示对该操作数取反。<br>
- 可以在右源寄存器后加上’<<‘, 表示对右源寄存器进行移位操作，左移的数量可能的值为{0, 1，2，3}， 左移0位时代表不做移位，可缺省。<br>
- 当右源操作对象Operand1为立即数时，支持常量值和立即数的取值操作：’%lo(表达式)‘表示获得表达式值的低12bit，’%tpcrel_lo(label)‘表示获得symbol地址相对于label表示TPC偏移值的低12bit, ‘%tprel_lo(symbl)’表是获得TLS变量相对于Thead Pointer寄存器的低12bit <br>

详细的微指令可以参见手册中[算术指令](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/arithmetic/)这一章节。

##汇编示例如下：<br>

```
add a1,a2, ->t        /* LL_GPR的R寄存器a1 + a2, 输出到LL_GPR的T寄存器 */
addi a1,4, ->t        /* LL_GPR的R寄存器a1 + 4, 输出到LL_GPR的T寄存器 */
add a1,a2.sw, ->t     /* 寄存器a1的值 + 寄存器a2截取寄存器的低32bit做有符号扩展的值, 输出到T寄存器 */
add a1,a2<<1, ->t     /* 寄存器a1的值 + 寄存器a2左移一位的值, 输出到T寄存器 */
add a1,a2.sw<<1,->t   /* 寄存器a1的值 + a2截取寄存器的低32bit做有符号扩展后左移一位的值， 输出到第二层的T寄存器 */
add a1,a2.sw<<1,->a1  /* 寄存器a1的值 + a2截取寄存器的低32bit做有符号扩展后左移一位的值， 输出到第一层GPR的a1寄存器 */
```
