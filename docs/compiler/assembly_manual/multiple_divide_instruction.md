# Multiplication instructions

```
Opcode Operand0,Operand1,->{LL_GPR, UL_GPR}     /* 输出到LL_GPR或者UL_GPR寄存器 */
```

- Add 'w' after Opcode: Opcode{w} indicates low 32-bit operation, and performs unsigned or signed operation and expansion depending on the presence or absence of 'u'. (0)<br>
- Add 'u' after Opcode: Opcode{u} indicates unsigned operation (1)<br>

For a description of the specific microinstructions, please refer to the chapter [Multiplication Instructions] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/mul_div/) in the manual.

Assembly example:<br>
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