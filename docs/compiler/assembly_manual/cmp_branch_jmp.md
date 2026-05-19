# Compare, branch, jump
## Comparison instructions
Usually there are two input operation objects, left source and right source, and one output

```
Opcode Operand0,Operand1,->{LL_GPR, UL_GPR}     /* 输出到LL_GPR或者UL_GPR中 */
```
Add: {.eq, .ne, .lt, .ge, .and, .or} after Opcode to indicate the conditions for the judgment to be established <br>

- '.eq' means that the judgment is true if they are equal. <br>
- '.ne' means that if they are not equal, the judgment will be established. <br>
- '.lt' means that the condition is true if the left source is smaller than the right source. <br>
- '.ge' means that the condition is true if the left source is greater than or equal to the right source. <br>
- '.and' means that the condition is true when both the left source and the right source are non-zero.
- '.or' means that the condition is true as long as one of the left source and the right source is non-zero.
- Adding 'u' to '.eq, .ne, .lt, .ge' indicates unsigned comparison.
- Adding 'i' to '.eq, .ne, .lt, .ge, .and, .or' indicates that the right source operation object is an immediate number`<br>

For detailed assembly microinstructions, please refer to the manual [Comparison Instructions] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/compare/).

Assembly instructions:

```
cmp.lt t#1, t#2, ->t                  /**/
cmp.ltu t#1, t#2, ->t                 /**/
cmp.lti t#1, 5, ->t                   /**/
```

## Branch instructions
Usually there are two input operation objects, left source and right source, and a branch jump target.

```
Opcode Operand0,Operand1,Operand2 
```

Add: {.eq, .ne, .lt, .ge} after Opcode to indicate the conditions for the judgment to be established <br>

- '.eq' means that if equal, the judgment is true<br>
- '.ne' means that if they are not equal, the judgment will be true<br>
- '.lt' means that the left source is smaller than the right source and the condition is true<br>
- '.ge' means that the condition is true if the left source is greater than or equal to the right source<br>
- Adding 'u' to this indicates an unsigned comparison. <br>

For detailed assembly microinstructions, please refer to [Intra-Block Jump Instructions] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/branch/).

Assembly instructions:

Operand2 is an immediate number and can be written in two forms: label (0) and immediate number (1). <br>
(0)
```
    .Ltogo:
    ...
    ...
    b.eq a1,a2,.Ltogo     /* 如果a1 == a2 成立，块内跳转到.Ltogo的位置  */
```

(1)
```
    b.eq a1,a2,0x20000    /* 如果a1 == a2 成立，块内跳转到0x20000的位置(0x20000为绝对地址) */
```

## Jump instructions

```
Opcode Operand0                    /*直接跳转，Operand0可以写成立即数或者符号*/
Opcode Operand0,Operand1           /*间接跳转*/
```

- When jumping directly, the operation object Operand0 is an immediate value<br>
- During indirect jump, the operation object Operand0 is a register and Operand1 is an immediate number. <br>

For detailed assembly microinstructions, please refer to [Intra-Block Jump Instructions] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/branch/).

Assembly example:

```
jr t#1, 4              /*跳转到t#1+4的位置*/
j .Ljump               /*直接跳转到.Ljump标签的位置*/
```