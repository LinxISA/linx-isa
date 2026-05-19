# 系统寄存器操作

```
Opcode Operand0, ->{LL_GPR, UL_GPR}               /* 输出到LL_GPR或者UL_GPR寄存器 */
Opcode Operand0, Operand1
Opcode Operand0, Operand1, ->{LL_GPR, UL_GPR}
```

'ssrget'和'ssrset'索引系统寄存器时需要使用系统寄存器的ID。详细的微指令描述可以参见手册中[系统寄存器访问指令](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/ssr_opration/)这一章节。

汇编示例：

```
loop.set a0, 1, ->LB0          /*将a0+1的值写到系统寄存器LB0中*/
ssrget 0x0010, ->t             /*加载tp寄存器的值到t刻度尺寄存器中*/

```
