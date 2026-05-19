# system registerOperation

```
Opcode Operand0, ->{LL_GPR, UL_GPR}               /* 输出到LL_GPR或者UL_GPR寄存器 */
Opcode Operand0, Operand1
Opcode Operand0, Operand1, ->{LL_GPR, UL_GPR}
```

'ssrget' and 'ssrset' need to use the ID of system register when indexing system register. For detailed microinstruction description, please refer to the chapter [system register Access Instructions] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/ssr_opration/) in the manual.

Assembly example:

```
loop.set a0, 1, ->LB0          /*将a0+1的值写到ZXTERMZH6QXZLB0中*/
ssrget 0x0010, ->t             /*加载tp寄存器的值到t刻度尺寄存器中*/

```