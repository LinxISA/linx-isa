# template block

```
MCOPY [Operand0, Operand1, Operand2] 
MSET [Operand0, Operand1, Operand2]
FENTRY [Operand0 ~ Operand1], sp!, operand2
FEXIT [Operand0 ~ Operand1], sp!, operand2
FRET.RA [Operand0 ~ Operand1], sp!, operand2
FRET.STK [Operand0 ~ Operand1], sp!, operand2
```

- It is recommended that the Opcode of template block uses uppercase, but lowercase is also supported.
- Operand0 and Operand1 in FENTRY, FEXIT, FRET.RA, FRET.STK give a register range, and the register ID is from Operand0 to Operand1. When Operand0 is greater than Operand1, the represented register range is [Operand0, 23], [2, Operand1].

For a specific description of template block instruction, please refer to the chapter [Template block instruction Collection] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/temp_block/intro/).

Example:<br>

```
MCOPY [a0, a1, a2]  /*将a1地址中a2个字节的数据拷贝到a0地址中*/
```