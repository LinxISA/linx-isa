# bit operation instructions

```
Opcode Operand0,Operand1,Operand2,->{LL_GPR,UL_GPR}     /* 输出到LL_GPR或者UL_GPR寄存器 */
```

Among them, Operand0 is the register operand, Operand1 and Operand2 are immediate operations. For detailed microinstruction description, please refer to the chapter [Bit Operation Instructions] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/bitmanip/) in the manual.

Example:

```
bxu a2,2,18,->a1          /*从a2寄存器中的第2位开始，截取18bit的数，即a2[19:2]，并无符号扩展到64bit，然后写入到a1寄存器*/
```