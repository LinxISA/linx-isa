# constant directive

```
Opcode Operand0,->{LL_GPR, UL_GPR}     /* 输出到LL_GPR或者UL_GPR */
```

For detailed microinstruction description, please refer to the chapter [Constant Instructions] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/inst/misa_g/LUI/).

Assembly example:

- Operand0 is an immediate number and supports constant value and immediate number value operations: %hi (expression) to obtain the 20-bit value of the expression, and the '%tpcrel_hi' table is to obtain the high 20-bit of the global symbol relative to the current TPC.

(0)
```
lui %hi(test), ->t    /* 获得标签’test‘地址，将其写入T寄存器  */
```

(1)
```
lui %hi(0x3fa80), ->t /* 获得0x3dfa80的高20bit，低12位默认为0，0x3f000写入T寄存器 */
```