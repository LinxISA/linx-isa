# Intra-block jump instructions

The jump instruction is used to jump between body instructions. The jump method supports **PC relative jump** and **register relative jump**.

## Command list

The list of jump instructions within the block is as follows:

| Microinstructions | Assembly format | Description |
|---------------|---------------|----------------------------------------|
| B.EQ | b.eq srcL, srcR, label | Determine whether to jump based on whether the left and right source operands are equal |
| B.NE | b.ne srcL, srcR, label | Determine whether to jump based on whether the left and right source operands are not equal |
| B.LT | b.lt srcL, srcR, label | Determine whether to jump based on whether the left source operand is less than the right source operand (signed comparison) |
| B.GE | b.ge srcL, srcR, label | Determine whether to jump based on whether the left source operand is greater than or equal to the right source operand (signed comparison) |
| B.LTU | b.ltu srcL, srcR, label | Determine whether to jump based on whether the left source operand is less than the right source operand (unsigned comparison) |
| B.GEU | b.geu srcL, srcR, label | Determine whether to jump based on whether the left source operand is greater than or equal to the right source operand (unsigned comparison) |
| B.Z | b.z label | Determine whether to jump based on whether the value of the P register is all zeros |
| B.NZ | b.z label | Determine whether to jump based on whether the value of the P register is non-all zero |
| JR | jr SrcL, label | Unconditionally jump to the target address of tpc plus offset in the register |
| J | j label | Unconditionally jump to the target address of the current tpc plus offset |

![InnerBlockBranch32bits](../../../figs/bitfield/svg/Introduction_32bit/BranchInstruction.svg)

## Remarks

1. This type of instruction has no destination register and does not occupy the block-private register.
3. When this type of instruction is the last instruction of body, block instruction will submit it immediately after this instruction is submitted, and the jump within the block will not take effect.