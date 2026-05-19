## scalar block private microinstructions

These microinstructions are only used by the scalar block. For a detailed description of the microinstructions, please refer to the chapter **scalarblock instruction Set**. The general assembly is as follows:

```
Opcode Operand0, Operand1, ->{LL_GPR, UL_GPR}
Opcode Operand0, Operand1, Operand2, ->{LL_GPR, UL_GPR}
Opcode Operand0, Operand1, Operand2, Operand3, ->{LL_GPR, UL_GPR}
Opcode [Operand0, Operand1]
Opcode [Operand0, Operand1], ->{LL_GPR, UL_GPR}
```