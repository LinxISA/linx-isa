#模板块

```
MCOPY [Operand0, Operand1, Operand2] 
MSET [Operand0, Operand1, Operand2]
FENTRY [Operand0 ~ Operand1], sp!, operand2
FEXIT [Operand0 ~ Operand1], sp!, operand2
FRET.RA [Operand0 ~ Operand1], sp!, operand2
FRET.STK [Operand0 ~ Operand1], sp!, operand2
```

- 建议模板块的Opcode使用大写，但小写也支持。
- FENTRY、FEXIT、FRET.RA、FRET.STK中的Operand0和Operand1给出一个寄存器范围，寄存器ID从Operand0到Operand1。当Operand0大于Operand1时，则表示的寄存器范围为[Operand0, 23]，[2, Operand1]。

具体的模版块指令描述可以参见[模板块指令集](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/temp_block/intro/)这一章节。

示例：<br>

```
MCOPY [a0, a1, a2]  /*将a1地址中a2个字节的数据拷贝到a0地址中*/
```
