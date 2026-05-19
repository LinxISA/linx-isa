# 位操作指令

```
Opcode Operand0,Operand1,Operand2,->{LL_GPR,UL_GPR}     /* 输出到LL_GPR或者UL_GPR寄存器 */
```

其中Operand0为寄存器操作数，Operand1和Operand2为立即数操作。细节的微指令描述可以参见手册中[位操作指令](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/bitmanip/)这一章节。

示例：

```
bxu a2,2,18,->a1          /*从a2寄存器中的第2位开始，截取18bit的数，即a2[19:2]，并无符号扩展到64bit，然后写入到a1寄存器*/
```
