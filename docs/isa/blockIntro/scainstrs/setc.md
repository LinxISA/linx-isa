# branch parameter setting command

The branch parameter setting instruction is used to determine the jump direction between blocks and calculate the jump direction of the next block when the block is submitted. Only suitable for block instruction types such as `条件跳转` and `间接跳转`.

For two-register input instructions, you can selectively intercept the low bits of the right source register with or without sign extension. Logical comparison instructions (setc.and and setc.or) can invert the right source register and then compare.

| Microinstructions | Assembly format | Description |
|-------------|--------------------------|-------------------------------------|
| SETC.EQ | setc.eq SrcL, SrcR<{.sw, .uw}> | Calculate the next header address based on whether the two operands are equal |
| SETC.NE | setc.ne SrcL, SrcR<{.sw, .uw}> | Calculate the next header address based on whether the two operands are not equal |
| SETC.AND | setc.and SrcL, SrcR<{.sw, .uw, .not}> | Calculate the next header address based on the logical AND result of the two operands |
| SETC.OR | setc.or SrcL, SrcR<{.sw, .uw, .not}> | Calculate the next header address based on the logical OR result of the two operands |
| SETC.LT | setc.lt SrcL, SrcR<{.sw, .uw}> | Calculate the next header address based on whether the left operand is less than the right operand (signed comparison) |
| SETC.GE | setc.ge SrcL, SrcR<{.sw, .uw}> | Calculate the next header address based on whether the left operand is greater than or equal to the right operand (signed comparison) |
| SETC.LTU | setc.ltu SrcL, SrcR<{.sw, .uw}> | Calculate the next header address based on whether the left operand is less than the right operand (unsigned comparison) |
| SETC.GEU | setc.geu SrcL, SrcR<{.sw, .uw}> | Calculate the next header address based on whether the left operand is greater than or equal to the right operand (unsigned comparison) |

The encoding format is as follows:

![Setcommit](../../../figs/bitfield/svg/Introduction_32bit/Setcommit.svg)| Microinstructions | Assembly format | Description |
|-------------|--------------------------|-------------------------------------|
| SETC.EQI | setc.eqi SrcL, simm | Calculate the next header address based on whether the left operand is equal to the signed immediate number |
| SETC.NEI | setc.nei SrcL, simm | Calculate the next header address based on whether the left operand is not equal to the signed immediate number |
| SETC.ANDI | setc.andi SrcL, simm | Calculate the next header address based on the logical AND result of the left operand and the signed immediate number |
| SETC.ORI | setc.ori SrcL, simm | Calculate the next header address based on the logical OR result of the left operand and the signed immediate value |
| SETC.LTI | setc.lti SrcL, simm | Calculate the next header address based on whether the left operand is less than the signed immediate number |
| SETC.GEI | setc.gei SrcL, simm | Calculate the next header address based on whether the left operand is greater than or equal to the signed immediate number |
| SETC.LTUI | setc.ltui SrcL, uimm | Calculate the next header address based on whether the left operand is less than the unsigned immediate number |
| SETC.GEUI | setc.geui SrcL, uimm | Calculate the next header address based on whether the left operand is greater than or equal to the unsigned immediate number |

The encoding format is as follows:

![Setwithimmediatecommit](../../../figs/bitfield/svg/Introduction_32bit/Setwithimmediatecommit.svg)