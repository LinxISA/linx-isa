## 标量块私有微指令

这些微指令仅限标量块使用，详细微指令的描述可以参见**标量块指令集**这一章节。通用汇编如下示意：

```
Opcode Operand0, Operand1, ->{LL_GPR, UL_GPR}
Opcode Operand0, Operand1, Operand2, ->{LL_GPR, UL_GPR}
Opcode Operand0, Operand1, Operand2, Operand3, ->{LL_GPR, UL_GPR}
Opcode [Operand0, Operand1]
Opcode [Operand0, Operand1], ->{LL_GPR, UL_GPR}
```

