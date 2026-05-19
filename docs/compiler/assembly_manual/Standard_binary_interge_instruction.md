# Standard binary integer arithmetic

Usually there are two input operation objects, left source and right source, and one output.

```
Opcode Operand0,Operand1,->{LL_GPR, UL_GPR}        /* 输出到块内寄存器或者全局寄存器 */
```

- Adding ‘w’ after Opcode indicates lower 32bit signed extension<br>
- Adding ‘i’ after Opcode indicates that the right source operation object is an immediate value<br>
- For arithmetic instructions, {.sw, .uw, .neg} extension can be added after the right source register. 'sw' means intercepting the lower 32 bits of the operand and doing signed extension. 'uw' means intercepting the lower 32 bits of the operand and doing unsigned extension. 'neg' means inverting the operand and adding 1<br>
- For logical logic operations, you can add {.sw, .uw, .not} extension after the right source register, '.not' means inverting the operand. <br>
- You can add '<<' after the right source register to indicate a shift operation on the right source register. The possible left shift values are {0, 1, 2, 3}. A left shift of 0 bits means no shift, which can be defaulted. <br>
- When the right source operation object Operaand1 is an immediate number, the value operation of constant value and immediate number is supported: '%lo(expression)' means to obtain the lower 12 bits of the expression value, '%tpcrel_lo(label)' means to obtain the lower 12 bits of the symbol address relative to the label, which represents the lower 12 bits of the TPC offset value, and the '%tprel_lo(symbl)' table is to obtain the lower 12 bits of the TLS variable relative to the Thead Pointer register <br>

For detailed microinstructions, please refer to the chapter [Arithmetic Instructions] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/arithmetic/) in the manual.

## Assembly examples are as follows:<br>

```
add a1,a2, ->t        /* LL_GPR的R寄存器a1 + a2, 输出到LL_GPR的T寄存器 */
addi a1,4, ->t        /* LL_GPR的R寄存器a1 + 4, 输出到LL_GPR的T寄存器 */
add a1,a2.sw, ->t     /* 寄存器a1的值 + 寄存器a2截取寄存器的低32bit做有符号扩展的值, 输出到T寄存器 */
add a1,a2<<1, ->t     /* 寄存器a1的值 + 寄存器a2左移一位的值, 输出到T寄存器 */
add a1,a2.sw<<1,->t   /* 寄存器a1的值 + a2截取寄存器的低32bit做有符号扩展后左移一位的值， 输出到第二层的T寄存器 */
add a1,a2.sw<<1,->a1  /* 寄存器a1的值 + a2截取寄存器的低32bit做有符号扩展后左移一位的值， 输出到第一层GPR的a1寄存器 */
```