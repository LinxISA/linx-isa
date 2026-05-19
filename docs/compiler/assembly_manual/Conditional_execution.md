# Status flags and conditional execution

Microinstructions of the 'setc' class are used to modify the CARG register. When block instruction is submitted, the corresponding path is executed based on the jump type of block instruction and the value in the CARG register. When the jump of block instruction is 'COND', 'IND', or 'ICALL', body needs to use the 'setc' microinstruction.

For example, you want to make a block jump to another block when a condition is met, and fall through to the next block if the condition is not met. The jump type and jump target address should be specified in header, which can be expressed with the 'BSTART.<type> COND, label' pseudo-instruction, and the 'setc' instruction of the conditional class is added to the body microinstruction to set the conditional state. For details of the CARG register, see [CARG register] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/register/common/bstate_com/?h=carg#carg). Examples are given below:

```
    ...
.Lblock1:
    BSTART COND, .Lblock2
    微指令
    setc.eq t#1, zero
    BSTART IND
    微指令
    setc.tgt t#1
    ...
    BSTART ICALL
    微指令
    addpc t#1,4,->ra
.Lblock2:
    BSTART
    ...
    BSTOP
    ...
```