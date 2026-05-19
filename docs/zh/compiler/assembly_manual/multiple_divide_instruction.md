# 乘法指令

```
Opcode Operand0,Operand1,->{LL_GPR, UL_GPR}     /* 输出到LL_GPR或者UL_GPR寄存器 */
```

- 在Opcode后面加上'w':Opcode{w}表明进行低32bit运算，根据有无'u'进行无符号或者有符号运算及扩展。 (0)<br>
- 在Opcode后面加上'u':Opcode{u}表明进行无符号操作 (1)<br>

具体的微指令的描述可以参见手册[乘法指令](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/mul_div/)这一章节。

汇编示例：<br>
(0) 
```
mulw a1,a2,->t      /* 有符号计算左源操作数的低32位乘以右源操作数的低32位，将结果的低32位有符号扩展后写到目的T寄存器中 */
muluw a1,a2,->t     /* 无符号计算左源操作数的低32位乘以右源操作数的低32位，将结果的低32位无符号扩展后写到目的T寄存器中 */
```

(1)
```
mulu a1,a2,->t        /* 无符号计算左源操作数乘以右源操作数，将结果的低64位写到目的T寄存器 */
mul a1,a2,->t        /* 有符号计算左源操作数乘以右源操作数，将结果的低64位写到目的T寄存器 */
```
